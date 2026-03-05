import base64
import os

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix


@Client.on_message(filters.command(["imgur"], prefix) & filters.me)
async def imgur(_, message: Message):
    # Check if a reply exists
    msg = await message.edit_text("🎉 Please wait. trying to upload...")
    if message.reply_to_message and message.reply_to_message.photo:
        # Download the photo
        photo_path = await message.reply_to_message.download()
        # Read the photo file and encode as base64
        with open(photo_path, "rb") as file:
            data = file.read()
            base64_data = base64.b64encode(data)
        # Set API endpoint and headers for image upload
        api_url = "https://api.imgur.com/3/image"
        api_headers = {"Authorization": "Client-ID a10ad04550b0648"}
        # Upload image to Imgur and get URL
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url, headers=api_headers, data={"image": base64_data}
            ) as resp:
                result = await resp.json()
        await msg.edit_text(result["data"]["link"])
    elif message.reply_to_message and message.reply_to_message.animation:
        # Download the animation (GIF)
        animation_path = await message.reply_to_message.download()
        # Read the animation file and encode as base64
        with open(animation_path, "rb") as file:
            data = file.read()
            base64_data = base64.b64encode(data)
        # Set API endpoint and headers for animation upload
        api_url = "https://api.imgur.com/3/image"
        api_headers = {"Authorization": "Client-ID a10ad04550b0648"}
        # Upload animation to Imgur and get URL
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url, headers=api_headers, data={"image": base64_data}
            ) as resp:
                result = await resp.json()
        await msg.edit_text(result["data"]["link"])
    else:
        await msg.edit_text(
            "Please reply to a photo or animation (GIF) to upload to Imgur."
        )


modules_help["imgur"] = {
    "imgur [img]*": "upload a photo or animation (GIF) to imgur",
}
