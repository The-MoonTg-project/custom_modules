from utils.scripts import import_library
from utils.config import cohere_key

cohere = import_library("cohere")

import cohere

co = cohere.Client(cohere_key)

from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from utils.db import db

from pyrogram import Client, filters, enums
from pyrogram.types import Message


@Client.on_message(filters.command("cohere", prefix) & filters.me)
async def cohere(c: Client, message: Message):
    try:
        chat_history = db.get_chat_history()

        if len(message.command) > 1:
            prompt = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
            prompt = message.reply_to_message.text
        else:
            await message.edit_text(
                f"<b>Usage: </b><code>{prefix}cohere [prompt/reply to message]</code>"
            )
            return

        db.add_chat_history({"role": "USER", "message": prompt})

        response = co.chat(
            chat_history=chat_history,
            model='command-r-plus',
            message=prompt,
            temperature=0.3,
            connectors=[{
                "id": "web-search",
                "options": {
                    "site": "wikipedia.com"
                }
            }],
            prompt_truncation="AUTO"
        )

        db.add_chat_history({"role": "CHATBOT", "message": response.text})

        await message.edit_text(f"**Question:**`{prompt}`\n**Answer:** {response.text}", parse_mode=enums.ParseMode.MARKDOWN)

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
