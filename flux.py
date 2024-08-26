import os
import io
import time
import aiohttp
import asyncio
import logging
from PIL import Image
from pyrogram import filters, Client
from pyrogram.types import Message
from concurrent.futures import ThreadPoolExecutor

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, progress

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API details
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
HUGGINGFACE_API_TOKEN = "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"

async def query_huggingface(payload):
    """Asynchronously send a request to the Hugging Face model with a timeout."""
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    timeout = aiohttp.ClientTimeout(total=60)  # Set a timeout of 60 seconds
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(HUGGINGFACE_API_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_message = await response.text()
                    logger.error(f"API Error - Status {response.status}: {error_message}")
                    return None
                return await response.read()
    except aiohttp.ClientError as e:
        logger.error(f"Network Error: {e}")
        return None

async def save_image(image_bytes, path):
    """Save the image bytes to a file asynchronously."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, save_image_sync, image_bytes, path)

def save_image_sync(image_bytes, path):
    """Save the image bytes to a file synchronously (used in thread pool)."""
    image = Image.open(io.BytesIO(image_bytes))
    image.save(path)

@Client.on_message(filters.command(["flux", "fl"], prefix) & filters.me)
async def imgflux_(client: Client, message: Message):
    """Handle the /flux command to generate and send an image."""
    prompt = message.text.split(" ", 1)[1] if len(message.command) > 1 else None
    if not prompt:
        return await message.reply_text("Please provide a prompt for Flux.")

    try:
        await message.edit_text("Processing...")

        # Generate the image asynchronously
        image_bytes = await query_huggingface({"inputs": prompt})
        if image_bytes is None:
            return await message.edit_text("Failed to generate an image.")

        # Save and send the image asynchronously
        image_path = "hf_flux_gen.jpg"
        await save_image(image_bytes, image_path)

        await message.reply_photo(image_path, progress=progress, progress_args=(message, time.time(), "Uploading image..."))

        # Clean up the saved image file
        if os.path.exists(image_path):
            os.remove(image_path)

        # Delete the processing message
        await message.delete()

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        await message.edit_text(format_exc(e))

# Help information for the module
modules_help["flux"] = {
    "flux [prompt]*": "Generate an AI image using FLUX",
    "fl [prompt]*": "Generate an AI image using FLUX"
}
