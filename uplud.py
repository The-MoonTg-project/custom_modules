import os
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library

@Client.on_message(filters.command(["upl"], prefix) & filters.me)
async def ytdl_handler(client: Client, message: Message):
try:
        file = message.command[1:]
    await message.edit("<b>Whom should I gmute?</b>")
    await message.reply(f"{file}")
