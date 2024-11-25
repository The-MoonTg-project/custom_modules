import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import prefix  # Importing prefix globally from utils.misc
import os

# Define modules_help at the top of the file to store help information for modules
modules_help = {}

# API endpoints
GOOGLE_LENS_URL = "https://lens.google.com/uploadbyurl?url="
GOOGLE_REVERSE_IMAGE_URL = "https://www.google.com/searchbyimage?sbisrc=4chanx&image_url={image}&safe=off"
API_FLASH_URL = "https://api.apiflash.com/v1/urltoimage?access_key=806cf941653948be8d8049defd086b82&url={query}&format=jpeg&full_page=true&no_cookie_banners=true&no_ads=true&no_tracking=true"

@Client.on_message(filters.command("lens", prefix) & filters.reply)
async def google_lens(_, message: Message):
    """Uploads the image, searches using Google Lens, and sends the screenshot of the results."""
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to an image with `.lens` to analyze it.")
        return

    processing_message = await message.reply_text("Processing the image with Google Lens...")

    try:
        photo_path = await message.reply_to_message.download()

        with open(photo_path, "rb") as image_file:
            response = requests.post("https://x0.at", files={"file": image_file})

        if response.status_code == 200:
            img_url = response.text.strip()
            lens_url = f"{GOOGLE_LENS_URL}{img_url}"
            screenshot_url = API_FLASH_URL.format(query=lens_url)

            caption = f"Here is the Google Lens result.\n[View Result]({lens_url})"
            await message.reply_photo(screenshot_url, caption=caption)
        else:
            await message.reply_text("Error: Could not upload the image.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        if photo_path:
            os.remove(photo_path)
        await processing_message.delete()

@Client.on_message(filters.command("reverse", prefix) & filters.reply)
async def google_reverse_search(_, message: Message):
    """Uploads the image, searches using Google Reverse Image Search, and sends the screenshot of the results."""
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to an image with `.reverse` to analyze it.")
        return

    processing_message = await message.reply_text("Processing the image with Google Reverse Image Search...")

    try:
        photo_path = await message.reply_to_message.download()

        with open(photo_path, "rb") as image_file:
            response = requests.post("https://x0.at", files={"file": image_file})

        if response.status_code == 200:
            img_url = response.text.strip()
            reverse_url = GOOGLE_REVERSE_IMAGE_URL.format(image=img_url)
            screenshot_url = API_FLASH_URL.format(query=reverse_url)

            caption = f"Here is the Google Reverse Image Search result.\n[View Result]({reverse_url})"
            await message.reply_photo(screenshot_url, caption=caption)
        else:
            await message.reply_text("Error: Could not upload the image.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        if photo_path:
            os.remove(photo_path)
        await processing_message.delete()

# Add module details to help
modules_help["google_image_search"] = {
    "lens": "Reply to a photo with `.lens` to analyze it using Google Lens and get a screenshot of the results.",
    "reverse": "Reply to a photo with `.reverse` to analyze it using Google Reverse Image Search and get a screenshot of the results."
          }
