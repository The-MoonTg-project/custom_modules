import os
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import prefix, modules_help
from utils.scripts import restart

@Client.on_message(filters.command("in", prefix) & filters.me)
async def in_f(client: Client, message: Message):
    if message.reply_to_message.document:
        module = await client.download_media(message.reply_to_message)
        if os.path.exists(module):
            shutil.copyfile(module, f"modules/custom_modules/{module}")
        await message.edit(f"<b>Module {module} downloaded succesfully restartin UB!</b>")
        restart()
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}dlf [reply to a file]</code>"
        )

@Client.on_message(filters.command("un", prefix) & filters.me)
async def un_f(client: Client, message: Message):
    if message.reply_to_message.document:
        module = message.reply_to_message.document.file_name
        if os.path.exists(f"modules/custom_modules/{module}"):
            os.remove(f"modules/custom_modules/{module}")
            await message.edit(f"<b>Module {module} removed succesfully restarting UB!</b>")
            restart()
        else:
            await message.edit(f"<b>Module {module} not found!</b>")
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}ulf [reply to a module name]</code>"
        )

modules_help = {
    "in [reply*]": "Download a module from telegram",
    "un [reply*]": "Remove a module from telegram"
}
