from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import prefix, modules_help


from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified
import os
import pygments
from pygments.formatters import ImageFormatter
from pygments.lexers import Python3Lexer


@Client.on_message(filters.command("ncode", prefix) & filters.me)
async def coder_print(client, message: Message):
    if message.reply_to_message:
        reply_message = message.reply_to_message
        if reply_message.media:
            download_path = await client.download_media(reply_message)
            with open(download_path, "r") as file:
                code = file.read()
            if os.path.exists(download_path):
                os.remove(download_path)
            pygments.highlight(
                f"{code}",
                Python3Lexer(),
                ImageFormatter(font_name="DejaVu Sans Mono", line_numbers=True),
                "result.png",
            )
            try:
                sent_message = await message.edit_text(
                    "Pasting this code on my page..."
                )
                await client.send_document(
                    chat_id=message.chat.id,
                    document="result.png",
                    caption="Code highlighted by Pygments",
                    reply_to_message_id=message.id,
                )
            except MessageNotModified:
                pass
            await sent_message.delete()
            if os.path.exists("result.png"):
                os.remove("result.png")
        else:
            return await message.reply_text("Please reply to a text or a file.")
    else:
        return await message.reply_text("Please reply to a text or a file.")


modules_help["ncode"] = {
    "ncode": "Highlight the code using Pygments and send it as an image."
}
