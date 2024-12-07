import os
import io
import time
import aiohttp
import asyncio
import logging
from PIL import Image

from pyrogram import filters, Client, enums
from pyrogram.types import Message

from concurrent.futures import ThreadPoolExecutor

from utils.db import db
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def query_huggingface(payload):
    api_key = db.get("custom.hf", "api_key", None)
    model = db.get("custom.hf", "current_model", None)

    if not api_key:
        raise ValueError(
            f"API key not set. Use {prefix}set_hf api <api_key> to set it."
        )
    if not model:
        raise ValueError(
            f"Model not set. Use {prefix}set_hf model <model_name> to set it."
        )

    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    timeout = aiohttp.ClientTimeout(total=120)
    start_time = time.time()
    retries = 3

    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    api_url, headers=headers, json=payload
                ) as response:
                    fetch_time = int((time.time() - start_time) * 1000)
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API Error {response.status}: {error_text}")
                        return None, fetch_time
                    return await response.read(), fetch_time
        except asyncio.TimeoutError:
            logger.error(f"TimeoutError: Attempt {attempt}/{retries} timed out.")
            if attempt == retries:
                raise
        except asyncio.CancelledError:
            logger.error(
                "Request was cancelled. Ensure the task is not being forcefully terminated."
            )
            raise
        except aiohttp.ClientError as e:
            logger.error(f"Network Error: {e}")
            if attempt == retries:
                raise
        finally:
            await asyncio.sleep(2)


async def save_image(image_bytes, path):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(
            pool, lambda: Image.open(io.BytesIO(image_bytes)).save(path)
        )


@Client.on_message(filters.command(["set_hf"], prefix) & filters.me)
async def manage_huggingface(_, message: Message):
    """Manage Hugging Face API key and models."""
    subcommand = message.command[1].lower() if len(message.command) > 1 else None
    arg = message.command[2] if len(message.command) > 2 else None

    if subcommand == "api":
        if arg:
            db.set("custom.hf", "api_key", arg)
            return await message.edit_text(
                f"Hugging Face API key set successfully.\nAPI Key: {arg}"
            )
        return await message.edit_text(f"Usage: {prefix}hf api <api_key>")

    if subcommand == "model":
        if arg:
            models = db.get("custom.hf", "models", [])
            if arg not in models:
                models.append(arg)
                db.set("custom.hf", "models", models)
            db.set("custom.hf", "current_model", arg)
            return await message.edit_text(
                f"Model '{arg}' added and set as the current model."
            )
        return await message.edit_text(f"Usage: {prefix}hf model <model_name>")

    if subcommand == "select":
        models = db.get("custom.hf", "models", [])
        if arg and arg.lower() == "all":
            db.set("custom.hf", "current_model", "all")
            model_list = "\n".join([f"*{i + 1}. {m}" for i, m in enumerate(models)])
            return await message.edit_text(
                f"All models selected:\n<code>{model_list}</code>\n\n"
                f"Images will be generated from all models."
            )
        if arg:
            try:
                index = int(arg) - 1
                if 0 <= index < len(models):
                    db.set("custom.hf", "current_model", models[index])
                    return await message.edit_text(f"Model set to '{models[index]}'.")
                return await message.edit_text("Invalid model number.")
            except ValueError:
                return await message.edit_text(
                    "Invalid model number. Use a valid integer."
                )
        return await message.edit_text(f"Usage: {prefix}hf select <model_number|all>")

    if subcommand == "delete" and arg:
        try:
            index = int(arg) - 1
            models = db.get("custom.hf", "models", [])
            if 0 <= index < len(models):
                removed_model = models.pop(index)
                db.set("custom.hf", "models", models)
                if db.get("custom.hf", "current_model") == removed_model:
                    db.set(
                        "custom.hf", "current_model", models[0] if models else "None"
                    )
                return await message.edit_text(f"Model '{removed_model}' deleted.")
            return await message.edit_text("Invalid model number.")
        except ValueError:
            return await message.edit_text("Invalid model number. Use a valid integer.")

    api_key = db.get("custom.hf", "api_key", None)
    models = db.get("custom.hf", "models", [])
    current_model = db.get("custom.hf", "current_model", "Not set")
    model_list = "\n".join(
        [
            f"{'*' if m == current_model or current_model == 'all' else ''}{i + 1}. {m}"
            for i, m in enumerate(models)
        ]
    )
    settings = (
        f"<b>Hugging Face settings:</b>\n"
        f"<b>API Key:</b>\n<code>{api_key if api_key else 'Not set'}</code>\n\n"
        f"<b>Available Models:</b>\n<code>{model_list}</code>"
    )
    usage_message = (
        f"{settings}\n\n<b>Usage:</b>\n"
        f"<code>{prefix}set_hf</code> <code>api</code>, <code>model</code>, <code>select</code>, <code>delete</code>, <code>select all</code>"
    )
    await message.edit_text(usage_message)


@Client.on_message(filters.command(["hf", "hface", "huggingface"], prefix))
async def imgflux_(_, message: Message):
    prompt = message.text.split(" ", 1)[1] if len(message.command) > 1 else None
    if not prompt:
        usage_message = (
            f"<b>Usage:</b> <code>{prefix}{message.command[0]} [custom prompt]</code>"
        )
        return await (
            message.edit_text if message.from_user.is_self else message.reply_text
        )(usage_message)

    processing_message = await (
        message.edit_text if message.from_user.is_self else message.reply_text
    )("Processing...")

    try:
        current_model = db.get("custom.hf", "current_model", None)
        models = db.get("custom.hf", "models", [])
        models_to_use = models if current_model == "all" else [current_model]

        generated_images = []

        for model in models_to_use:
            db.set("custom.hf", "current_model", model)
            payload = {"inputs": prompt}
            image_bytes, fetch_time = await query_huggingface(payload)
            if not image_bytes:
                logger.warning(f"Failed to fetch image for model: {model}")
                continue

            image_path = f"hf_flux_gen_{model.replace('/', '_')}.jpg"
            await save_image(image_bytes, image_path)
            generated_images.append((image_path, model, fetch_time))

        if not generated_images:
            return await processing_message.edit_text(
                "Failed to generate an image for all models."
            )

        for image_path, model_name, fetch_time in generated_images:
            caption = (
                f"**Model:**\n> {model_name}\n"
                f"**Prompt used:**\n> {prompt}\n\n"
                f"**Fetching Time:** {fetch_time} ms"
            )
            await message.reply_photo(
                image_path, caption=caption, parse_mode=enums.ParseMode.MARKDOWN
            )
            os.remove(image_path)

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        await processing_message.edit_text(format_exc(e))
    finally:
        await processing_message.delete()


modules_help["huggingface"] = {
    "hf [prompt]*": "Generate an AI image using Hugging Face model(s).",
    "set_hf <api>*": "Set the Hugging Face API key.",
    "set_hf model <model_name>*": "Add and set a Hugging Face model.",
    "set_hf select <model_number|all>*": "Select a specific model or all models for use.",
    "set_hf delete <model_number>*": "Delete a model from the list.",
}
