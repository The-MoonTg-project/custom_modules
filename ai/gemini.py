# This scripts contains use cases for userbots
# This is used on my Moon-Userbot: https://github.com/The-MoonTg-project/Moon-Userbot
# YOu can check it out for uses example
import os
import io

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from PIL import Image

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library
from utils.config import gemini_key
from utils.rentry import paste as rentry_paste

genai = import_library("google.generativeai", "google-generativeai")

genai.configure(api_key=gemini_key)

model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
system_prompt = os.environ.get("GEMINI_SYSTEM_PROMPT", "You are a helpful AI assistant.")
safety_settings = {
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
}
model = genai.GenerativeModel(
    model_name, safety_settings=safety_settings, system_instruction=system_prompt
)


@Client.on_message(filters.command("gemini", prefix) & filters.me)
async def say(client: Client, message: Message):
    try:
        await message.edit_text("<code>Thinking...</code>")

        command_text = message.text or message.caption or ""
        prompt = ""
        parts = command_text.split(maxsplit=1)
        if len(parts) > 1:
            prompt = parts[1]
        elif message.reply_to_message:
            prompt = (
                message.reply_to_message.text
                or message.reply_to_message.caption
                or ""
            )

        image_part = None
        photo = message.photo or (
            message.reply_to_message and message.reply_to_message.photo
        )

        if photo:
            image_stream = await client.download_media(photo, in_memory=True)
            if image_stream:
                try:
                    pil_image = Image.open(image_stream)
                    image_part = pil_image
                except Exception as e:
                    await message.edit_text(
                        f"<b>Error:</b> <code>Failed to process image: {e}</code>"
                    )
                    return

        if not prompt and not image_part:
            await message.edit_text(
                f"<b>Usage: </b><code>{prefix}gemini [prompt/reply to message with text or image]</code>"
            )
            return

        contents = []
        if prompt:
            contents.append(prompt)
        if image_part:
            contents.append(image_part)

        response = model.generate_content(contents)

        output_text = response.text
        if prompt:
            processed_prompt = prompt.replace('\n', '\n> ')
            question_text = f"👤**Prompt:**\n> {processed_prompt}"
        else:
            question_text = ""

        processed_response = output_text.replace('\n', '\n> ')
        formatted_response = f"🤖**Response:**\n> {processed_response}"

        await message.edit_text(
            f"{question_text}\n{formatted_response}\nPowered by Gemini",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    except MessageTooLong:
        await message.edit_text(
            "<code>Output is too long... Pasting to rentry...</code>"
        )
        try:
            rentry_url, edit_code = await rentry_paste(
                text=f"{response.text}\n\nPowered by Gemini", return_edit=True
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
