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

    await message.edit("<b>Uploading...</b>")
    file_name = "/" + link.split("/")[-1]

    try:
        resp = requests.get(link)
        resp.raise_for_status()

        with open(file_name, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        await message.edit("<b>Uploading Now...</b>")
        await client.send_document(message.chat.id, file_name)
        await message.delete()
    except Exception as e:
        await message.edit(format_exc(e))
    finally:
        os.remove(file_name)
