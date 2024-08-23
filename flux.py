 
import os
import time
import requests
from pyrogram import filters, Client
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, progress

def schellwithflux(args):
    API_URL = "https://randydev-ryuzaki-api.hf.space/api/v1/akeno/fluxai"
    api_key = "6398769dabd9fe0e49bedce0354b40a9b1a69d9594dc9d48c1d8a2a071c51e89"
    payload = {
        "user_id": 1191668125,  # Please don't edit here
        "args": args,
        "api_key": api_key  # Add the API key to the payload
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code != 200:
        print(f"Error status {response.status_code}: {response.text}")
        return None
    return response.content

@Client.on_message(filters.command("flux", prefix) & filters.me)
async def imgfluxai_(client: Client, message: Message):
    question = message.text.split(" ", 1)[1] if len(message.command) > 1 else None
    if not question:
        return await message.reply_text("Please provide a question for Flux.")
    try:
        await message.edit_text("Generating image, please wait...")
        
        image_bytes = schellwithflux(question)
        if image_bytes is None:
            return await message.edit_text("Failed to generate an image.")
        
        # Save the image to disk
        with open("flux_gen.jpg", "wb") as f:
            f.write(image_bytes)
        
        await message.edit_text("Uploading image...")
        await message.reply_photo("flux_gen.jpg", progress=progress, progress_args=(message, time.time(), "Uploading image..."))
        
        # Clean up the file after uploading
        if os.path.exists("flux_gen.jpg"):
            os.remove("flux_gen.jpg")
        
        # Delete the original message after everything is done
        await message.delete()
        
    except Exception as e:
        await message.edit_text(format_exc(e))

modules_help["fluxai"] = {
    "flux [prompt]*": "text to image fluxai",
            }
