# This scripts contains use cases for userbots
# This is used on my Moon-Userbot: https://github.com/The-MoonTg-project/Moon-Userbot
# YOu can check it out for uses example
import os
import PIL.Image
import google.generativeai as genai

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library
from utils.config import gemini_key

genai.configure(api_key=gemini_key)

model = genai.GenerativeModel("gemini-pro-vision")


@Client.on_message(filters.command("ocrai", prefix) & filters.me)
async def ocrai(_, message: Message):
    try:
        await message.edit_text("<code>Please Wait...</code>")
        base_img = await message.reply_to_message.download()

        img = PIL.Image.open(base_img)
        ocr = [
        "OCR the given image with precison and accuracy",
        img,
        ]

        response = model.generate_content(ocr)

        await message.edit_text(
            f"**Detail Of Image:** {response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        os.remove(base_img)


modules_help["ocrai"] = {
    "ocrai [reply to image]*": "OCR Ai with gemini",
}
