# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# MoonUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2023-2024 by MoonUserBot@Github.

# This file is part of: https://github.com/The-Moon-Userbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/The-Moon-Userbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import warnings
import os
import sys
import asyncio
import subprocess

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# Suppress specific warnings from lottie
warnings.filterwarnings("ignore", message="Merge paths are not supported")

# Check and install required packages
try:
    import lottie
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lottie"])

@Client.on_message(filters.command(["destroy"], prefix) & filters.me)
async def destroy_sticker(client: Client, message: Message):
    """Destroy animated stickers by modifying their animation properties"""
    try:
        # Verify lottie tools are available
        if not os.path.exists(sys.executable.replace("python", "lottie_convert.py")):
            await message.edit("**Installing required tools...**", parse_mode=enums.ParseMode.MARKDOWN)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "lottie"])

        reply = message.reply_to_message
        if not reply or not reply.sticker or not reply.sticker.is_animated:
            return await message.edit(
                "**Please reply to an animated sticker!**",
                parse_mode=enums.ParseMode.MARKDOWN
            )

        edit_msg = await message.edit("**🔄 Destroying sticker...**", parse_mode=enums.ParseMode.MARKDOWN)

        # Download sticker
        tgs_path = await client.download_media(reply)
        if not tgs_path or not os.path.exists(tgs_path):
            return await edit_msg.edit("**❌ Download failed!**", parse_mode=enums.ParseMode.MARKDOWN)

        # Conversion process
        json_path = "temp.json"
        output_path = "MoonUB.tgs"

        os.system(f"lottie_convert.py {tgs_path} {json_path}")
        if not os.path.exists(json_path):
            return await edit_msg.edit("**❌ JSON conversion failed!**", parse_mode=enums.ParseMode.MARKDOWN)

        # Modify JSON data
        with open(json_path, "r+") as f:
            content = f.read()
            modified = content.replace("[1]", "[2]") \
                              .replace("[2]", "[3]") \
                              .replace("[3]", "[4]") \
                              .replace("[4]", "[5]") \
                              .replace("[5]", "[6]")
            f.seek(0)
            f.write(modified)
            f.truncate()

        # Convert back to TGS
        os.system(f"lottie_convert.py {json_path} {output_path}")
        if not os.path.exists(output_path):
            return await edit_msg.edit("**❌ Final conversion failed!**", parse_mode=enums.ParseMode.MARKDOWN)

        # Send result
        await message.reply_document(
            output_path,
            reply_to_message_id=reply.id
        )
        await edit_msg.delete()

    except Exception as e:
        await message.edit(f"**❌ Error:** `{e}`", parse_mode=enums.ParseMode.MARKDOWN)
    finally:
        # Cleanup temporary files
        for file_path in [tgs_path, json_path, output_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as clean_error:
                    print(f"Cleanup error: {clean_error}")

# ================================== Help Module ================================== #
modules_help["sticker_tools"] = {
    "destroy [reply]": "Modify and destroy animated stickers"
}
