# This scripts contains use cases for userbots
# This is used on my Moon-Userbot: https://github.com/The-MoonTg-project/Moon-Userbot
# YOu can check it out for uses example
import os

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library
from utils.config import gemini_key
from utils.rentry import paste as rentry_paste

genai = import_library("google.generativeai", "google-generativeai")

genai.configure(api_key=gemini_key)

model = genai.GenerativeModel("gemini-2.0-flash")


@Client.on_message(filters.command("gemini", prefix) & filters.me)
async def say(client: Client, message: Message):
    try:
        await message.edit_text("<code>Please Wait...</code>")

        if len(message.command) > 1:
            prompt = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
            prompt = message.reply_to_message.text
        else:
            await message.edit_text(
                f"<b>Usage: </b><code>{prefix}gemini [prompt/reply to message]</code>"
            )
            return

        chat = model.start_chat()
        response = chat.send_message(prompt)

        await message.edit_text(
            f"**Question:**`{prompt}`\n**Answer:** {response.text}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    except MessageTooLong:
        await message.edit_text(
            "<code>Output is too long... Pasting to rentry...</code>"
        )
        try:
            rentry_url, edit_code = await rentry_paste(
                text=response.text, return_edit=True
            )
        except RuntimeError:
            await message.edit_text(
                "<b>Error:</b> <code>Failed to paste to rentry</code>"
            )
            return
        await client.send_message(
            "me",
            f"Here's your edit code for Url: {rentry_url}\nEdit code:  <code>{edit_code}</code>",
            disable_web_page_preview=True,
        )
        await message.edit_text(
            f"<b>Output:</b> {rentry_url}\n<b>Note:</b> <code>Edit Code has been sent to your saved messages</code>",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


modules_help["gemini"] = {
    "gemini [prompt]*": "Ask questions with Gemini Ai",
}
