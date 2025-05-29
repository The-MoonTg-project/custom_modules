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
#

from pyrogram import Client, filters, enums
from pyrogram.types import Message
import requests
import os
from utils.misc import modules_help, prefix

# Configuration
IMG_BB_API_KEY = "edf3ffaf984fb9c0f5bf224d40cf54b9"  # Get from https://api.imgbb.com/
BASE_URL = "https://api.imgbb.com/1/upload"

@Client.on_message(filters.command("imgbb", prefix) & filters.me)
async def imgbb_upload(client: Client, message: Message):
    # @Tech_Shreyansh1
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo
    elif message.photo:
        photo = message.photo
    else:
        await message.edit("<b>Reply to an image or send image with command</b>")
        return

    try:
        # Download the photo
        photo_path = await client.download_media(photo)
        
        # Upload to ImgBB
        with open(photo_path, "rb") as image_file:
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
            
            await message.edit(
                f"<b>Image Uploaded Successfully!</b>\n\n"
                f"<b>URL:</b> <code>{image_url}</code>\n"
                f"<b>Delete URL:</b> <code>{delete_url}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.edit(f"<b>Upload failed with status {response.status_code}</b>")
        
        # Clean up downloaded file
        os.remove(photo_path)
        
    except Exception as e:
        await message.edit(f"<b>Error:</b> <code>{str(e)}</code>")

modules_help["imgbb"] = {
    "imgbb": "Upload image to ImgBB (reply to image or send with command). Returns URL and delete URL."
}

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
#
