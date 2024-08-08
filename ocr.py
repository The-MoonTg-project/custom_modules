import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import os
from utils.db import db
from utils.misc import modules_help, prefix

OCR_SPACE_API_KEY = db.get("custom.ocr", "ocr_api", None)
OCR_SPACE_URL = "https://api.ocr.space/parse/image"


@Client.on_message(filters.command(["set_ocrapi"], prefix) & filters.me)
async def ocr_space_api(_, message: Message):
    if OCR_SPACE_API_KEY is not None:
        return await message.edit_text(f"OCRSPACE API key is already set")
    if len(message.command) > 1:
        api_key = message.text.split(maxsplit=1)[1]
        db.set("custom.ocr", "ocr_api", api_key)
        return await message.edit_text(f"OCRSPACE API key set success")


@Client.on_message(filters.command(["ocr"], prefix) & filters.me)
async def ocr_space(_, message: Message):
    if OCR_SPACE_API_KEY is None:
        return await message.edit_text(f"OCRSPACE API key isn't set, please set it using `<code>{prefix}set_ocrapi <your_api></code> command")
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.edit(f"Reply to an image with <code>{prefix}ocr</code> command to extract text.")
        return

    await message.edit("Processing image...")

    photo = await message.reply_to_message.download()
    try:
        with open(photo, 'rb') as image_file:
            response = requests.post(
                OCR_SPACE_URL,
                files={"file": image_file},
                data={"apikey": OCR_SPACE_API_KEY},
                timeout=10  # Optional timeout
            )

        if response.status_code == 200:
            result = response.json()
            if result["IsErroredOnProcessing"]:
                await message.edit("Error occurred during OCR processing. Please try again.")
            else:
                parsed_text = result["ParsedResults"][0]["ParsedText"]
                await message.edit(f"Extracted Text:\n{parsed_text}")
        else:
            await message.edit("An error occurred, please try again later.")
    except Exception as e:
        await message.edit("An unexpected error occurred.")
        print(f"Error: {e}")
    finally:
        if os.path.exists(photo):
            os.remove(photo)  # Clean up the downloaded file


modules_help["ocr"] = {
    "ocr [reply to image]*": "Reply to an image with this command to extract text from it using OCR.Space API."
}
