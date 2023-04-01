import os
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library


@Client.on_message(filters.command(["upk"], prefix) & filters.me)
async def upl(client: Client, message: Message):
    file = message.command[1:]
    await message.edit(f"<b>Uploading{file}</b>")
    await message.reply_document(f"{file]}.mkv")
