import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import os

from utils.misc import modules_help, prefix

OCR_SPACE_API_KEY = "K83738930788957"
OCR_SPACE_URL = "https://api.ocr.space/parse/image"


@Client.on_message(filters.command(["ocr"], prefix) & filters.me)
async def ocr_space(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.edit("Reply to an image with `ocr` command to extract text.")
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
        os.remove(photo)  # Clean up the downloaded file

modules_help["ocr"] = {
    "ocr": "Reply to an image with this command to extract text from it using OCR.Space API."
}
