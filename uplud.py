import os

from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command("upl", prefix) & filters.me)
async def urldl(client: Client, message: Message):
    if len(message.command) > 1:
        link = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        link = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}upl [filepath to upload]</code>"
        )
        return

    try:
        
        await message.edit("<b>Uploading Now...</b>")
        await client.send_document(message.chat.id, link)
        await message.delete()
    except Exception as e:
        await message.edit(format_exc(e))
    finally:
        os.remove(link)

modules_help["uplud"] = {
    "uplud": f"[filepath]/[reply to path]*"
}
