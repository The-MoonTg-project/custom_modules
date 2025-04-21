import os
import aiohttp
import asyncio
import logging
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from concurrent.futures import ThreadPoolExecutor
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ENDPOINTS = {
    "AI4Chat": "https://api.nekorinn.my.id/ai-img/ai4chat",
    "FLUX": "https://api.nekorinn.my.id/ai-img/flux",
    "Text2Img-V2": "https://api.nekorinn.my.id/ai-img/text2img-v2",
    "DeepImg": "https://api.nekorinn.my.id/ai-img/deep-img",  # Single-prompt endpoint
    "GeminiImage": "https://api.nekorinn.my.id/ai-img/gemini-image",  # Single-prompt endpoint with retry
    "Imagen": "https://api.nekorinn.my.id/ai-img/imagen",  # Single-prompt endpoint
}

AVAILABLE_RATIOS = ["1:1", "16:9", "2:3", "3:2", "4:5", "5:4", "9:16", "21:9", "9:21"]
DELAY_BETWEEN_REQUESTS = 2
MAX_RETRIES = 3

async def fetch_image(endpoint_name, prompt, ratio=None, retries=0):
    if endpoint_name in ["DeepImg", "GeminiImage", "Imagen"]:
        url = f"{API_ENDPOINTS[endpoint_name]}?text={prompt}"
    else:
        url = f"{API_ENDPOINTS[endpoint_name]}?text={prompt}&ratio={ratio}"
    
    timeout = aiohttp.ClientTimeout(total=60)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API Error for {endpoint_name} ({ratio}): {response.status} - {error_text}")

                    if endpoint_name == "GeminiImage" and retries < MAX_RETRIES:
                        logger.warning(f"Retrying {endpoint_name} (Attempt {retries + 1}/{MAX_RETRIES})...")
                        await asyncio.sleep(1) 
                        return await fetch_image(endpoint_name, prompt, ratio, retries + 1)

                    return None, error_text
                return await response.read(), None
    except aiohttp.ClientError as e:
        logger.error(f"Network Error for {endpoint_name} ({ratio}): {e}")
        return None, str(e)

async def save_image(image_bytes, path):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, lambda: open(path, "wb").write(image_bytes))

@Client.on_message(filters.command(["imager", "im"], prefix))
async def generate_images(client: Client, message: Message):
    prompt = message.text.split(" ", 1)[1] if len(message.command) > 1 else None
    if not prompt:
        usage_message = f"<b>Usage:</b> <code>{prefix}{message.command[0]} [custom prompt]</code>"
        return await (message.edit_text if message.from_user.is_self else message.reply_text)(usage_message)

    processing_message = await (message.edit_text if message.from_user.is_self else message.reply_text)("Generating images...")

    try:
        for endpoint_name in API_ENDPOINTS:
            if endpoint_name in ["DeepImg", "GeminiImage", "Imagen"]:
                for i in range(9):
                    image_bytes, error_message = await fetch_image(endpoint_name, prompt)
                    if not image_bytes:
                        if endpoint_name == "GeminiImage":
                            logger.warning(f"Skipping {endpoint_name} after {MAX_RETRIES} retries.")
                            continue

                        logger.error(f"Failed to fetch image for {endpoint_name}: {error_message}")
                        await message.reply_text(f"Failed to generate image for {endpoint_name}.\nError: {error_message}")
                        continue

                    image_path = f"generated_image_{endpoint_name}_{i + 1}.jpg"
                    await save_image(image_bytes, image_path)

                    await message.reply_photo(
                        image_path,
                        caption=f"**Endpoint:** {endpoint_name}\n**Prompt:** {prompt}\n**Image Number:** {i + 1}",
                        parse_mode=enums.ParseMode.MARKDOWN,
                    )

                    os.remove(image_path)

                    await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
            else:
                for ratio in AVAILABLE_RATIOS:
                    image_bytes, error_message = await fetch_image(endpoint_name, prompt, ratio)
                    if not image_bytes:
                        logger.error(f"Failed to fetch image for {endpoint_name} with ratio {ratio}: {error_message}")
                        await message.reply_text(f"Failed to generate image for {endpoint_name} with ratio {ratio}.\nError: {error_message}")
                        continue

                    image_path = f"generated_image_{endpoint_name}_{ratio.replace(':', '_')}.jpg"
                    await save_image(image_bytes, image_path)

                    await message.reply_photo(
                        image_path,
                        caption=f"**Endpoint:** {endpoint_name}\n**Prompt:** {prompt}\n**Ratio:** {ratio}",
                        parse_mode=enums.ParseMode.MARKDOWN,
                    )

                    os.remove(image_path)

                    await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        await processing_message.edit_text(format_exc(e))
    finally:
        await processing_message.delete()

modules_help["imager"] = {
    "imager [custom prompt]*": "Generate AI images for all ratios using the AI4Chat, FLUX, Text2Img-V2, DeepImg, GeminiImage, and Imagen APIs",
    "im [custom prompt]*": "Generate AI images for all ratios using the AI4Chat, FLUX, Text2Img-V2, DeepImg, GeminiImage, and Imagen APIs"
}
