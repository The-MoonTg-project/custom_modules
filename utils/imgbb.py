import base64
import json
import os
from io import BytesIO

import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.db import db
from utils.scripts import format_exc

from utils import modules_help, prefix


@Client.on_message(filters.command("set_imgbb_api", prefix) & filters.me)
async def set_imgbb_api(_, message: Message):
    if len(message.command) < 2:
        return await message.edit_text(
            f"<b>Usage:</b> <code>{prefix}set_imgbb_api [api_key]*</code>",
            parse_mode=enums.ParseMode.HTML,
        )
    api_key = message.text.split(maxsplit=1)[1]
    db.set("custom.imgbb", "api", api_key)
    return await message.edit_text(
        f"imgbb api set to <code>{api_key}</code>", parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["imgbb", "ibb"], prefix) & filters.me)
async def imgbb_up(client: Client, message: Message):
    imgbb_api = db.get("custom.imgbb", "api", None)
    if imgbb_api is None:
        return await message.edit_text("imgbb api not set, use set_imgbb_api command")

    reply = message.reply_to_message
    if not reply:
        return await message.edit_text("Reply to an image to upload")

    ms = await message.edit_text(
        "<b>Processing...</b>", parse_mode=enums.ParseMode.HTML
    )
    path = await client.download_media(reply)

    if not path:
        return await ms.edit_text("Failed to download media")

    try:
        with open(path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": imgbb_api,
            "image": img_data,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as resp:
                result = await resp.json()

        if result.get("success"):
            data = result["data"]
            image_url = data["url"]
            delete_url = data["delete_url"]
            await ms.edit_text(
                f"<b>Image URL:</b> <code>{image_url}</code>\n"
                f"<b>Delete URL:</b> <code>{delete_url}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        else:
            await ms.edit_text(
                f"Upload failed: {result.get('error', {}).get('message', 'Unknown error')}"
            )
    except Exception as e:
        await ms.edit_text(format_exc(e))
    finally:
        if os.path.exists(path):
            os.remove(path)


modules_help["imgbb"] = {
    "imgbb [reply to image]*": "Upload image to imgbb",
    "set_imgbb_api [api_key]*": "Set imgbb API key",
}
