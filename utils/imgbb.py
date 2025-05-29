# Don't Remove Credit @Tech_Shreyansh29, @MrGhostsx
# Ask Doubt on telegram @ShreyanshSupport2
#
# Copyright (C) 2025 by MrGhostsx@Github, < https://github.com/TechyShreyansh>.
#
# This file is part of < https://github.com/TechyShreyansh > project,
# and is released under the MIT License.
# Please see < https://github.com/TechyShreyansh/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import Client, filters, enums
from pyrogram.types import Message
import requests
import os
from utils.misc import modules_help, prefix

# Configuration
IMG_BB_API_KEY = "edf3ffaf984fb9c0f5bf224d40cf54b9"  # Get from https://api.imgbb.com/
BASE_URL = "https://api.imgbb.com/1/upload"
SUPPORTED_MIME_TYPES = [
    'image/jpeg', 'image/png', 'image/gif', 
    'image/webp', 'image/bmp', 'image/x-icon'
]

@Client.on_message(filters.command("imgbb", prefix) & filters.me)
async def imgbb_upload(client: Client, message: Message):
    # Check for supported media types
    media = None
    if message.reply_to_message:
        if message.reply_to_message.photo:
            media = message.reply_to_message.photo
        elif (message.reply_to_message.document and 
              message.reply_to_message.document.mime_type in SUPPORTED_MIME_TYPES):
            media = message.reply_to_message.document
    elif message.photo:
        media = message.photo
    elif (message.document and 
          message.document.mime_type in SUPPORTED_MIME_TYPES):
        media = message.document
    
    if not media:
        await message.edit(
            "<b>Reply to an image or send image with command</b>\n"
            "<i>Supported formats: JPEG, PNG, GIF, WEBP, BMP, ICO</i>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    try:
        # Download the media
        media_path = await client.download_media(media)
        
        # Upload to ImgBB (without expiration)
        with open(media_path, "rb") as image_file:
            response = requests.post(
                BASE_URL,
                params={"key": IMG_BB_API_KEY},
                files={"image": image_file}
            )
        
        # Process response
        if response.status_code == 200:
            data = response.json()
            image_url = data["data"]["url"]
            delete_url = data["data"]["delete_url"]
            thumb_url = data["data"]["thumb"]["url"] if "thumb" in data["data"] else image_url
            
            await message.edit(
                f"<b>📁 Image Uploaded Successfully!</b>\n\n"
                f"<b>🔗 Permanent URL:</b> <code>{image_url}</code>\n"
                f"<b>🖼️ Thumbnail:</b> <code>{thumb_url}</code>\n"
                f"<b>🗑️ Delete URL:</b> <code>{delete_url}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.edit(f"<b>❌ Upload failed with status {response.status_code}</b>")
        
        # Clean up downloaded file
        os.remove(media_path)
        
    except Exception as e:
        await message.edit(f"<b>❌ Error:</b> <code>{str(e)}</code>")

modules_help["imgbb"] = {
    "imgbb": "Upload any image (JPEG/PNG/GIF/WEBP/BMP/ICO) to ImgBB."
            }
