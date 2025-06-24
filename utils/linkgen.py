#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
from pyrogram import Client, filters
from pyrogram.errors import UserBlocked
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from utils.db import db

BOT_KEY = "LINKGEN_BOT"

def is_supported_media(message: Message) -> bool:
    return bool(message.audio or message.document or message.video)

async def get_file_link(client: Client, file_message: Message, bot_username: str) -> str:
    try:
        forwarded = await file_message.forward(bot_username)
        await asyncio.sleep(3)
        async for msg in client.get_chat_history(bot_username, limit=1):
            if msg.text and "http" in msg.text:
                return msg.text
        return "No response from bot"
    except UserBlocked:
        return f"❌ <b>Please unblock</b> <code>{bot_username}</code> <b>first</b>"
    except Exception as e:
        return f"<b>Error:</b> <i>{format_exc(e)}</i>"

@Client.on_message(filters.command("l", prefix) & filters.me)
async def generate_link(client: Client, message: Message):
    replied = message.reply_to_message
<<<<<<< HEAD
    bot_username = db.get("linkgen", BOT_KEY)
=======
    bot_username = db.get("custom.linkgen", BOT_KEY)
>>>>>>> 206d9f27e3e0d8f47a6602c67d8aa6341a4cea26

    if not bot_username:
        return await message.edit(f"❌ <b>No bot set.</b> Use <code>{prefix}addbot @botusername</code> first.")

    if not replied:
        return await message.edit("<b>❌ Reply to a supported file</b> (audio/document/video).")

    if not is_supported_media(replied):
        return await message.edit("<b>❌ Unsupported file type.</b>")

    status_msg = await message.edit("<i>⏳ Generating download link...</i>")

    try:
        link = await get_file_link(client, replied, bot_username)
        await status_msg.edit(f"<b>✅ Download Link:</b>\n\n<code>{link}</code>")
    except Exception as e:
        await status_msg.edit(f"<b>⚠️ Error:</b> <i>{format_exc(e)}</i>")

@Client.on_message(filters.command("addbot", prefix) & filters.me)
async def add_bot(_, message: Message):
    if len(message.command) < 2:
        return await message.edit(f"❌ <b>Usage:</b> <code>{prefix}addbot @botusername</code>")
    
    bot_username = message.command[1]
    if not bot_username.startswith("@"):
        return await message.edit("❌ <b>Please provide a valid bot username starting with</b> <code>@</code>")
    
<<<<<<< HEAD
    db.set("linkgen", BOT_KEY, bot_username)
=======
    db.set("custom.linkgen", BOT_KEY, bot_username)
>>>>>>> 206d9f27e3e0d8f47a6602c67d8aa6341a4cea26
    await message.edit(f"✅ <b>Bot set to:</b> <code>{bot_username}</code>")

@Client.on_message(filters.command("delbot", prefix) & filters.me)
async def delete_bot(_, message: Message):
<<<<<<< HEAD
    db.set("linkgen", BOT_KEY, None)
=======
    db.set("custom.linkgen", BOT_KEY, None)
>>>>>>> 206d9f27e3e0d8f47a6602c67d8aa6341a4cea26
    await message.edit(f"✅ <b>Bot removed successfully.</b>\nYou can add again using <code>{prefix}addbot @botusername</code>.")

modules_help["linkgen"] = {
    "l [reply]": "Generate direct download link for audio/document/video files",
    "addbot @botusername": "Set bot used to generate file links",
    "delbot": "Remove currently set bot"
}
