import os
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import import_library
from utils.config import gemini_key


import_library("pyzerox", "py-zerox")

from pyzerox import zerox
from pyzerox.errors import ModelAccessError, NotAVisionModel
import litellm

kwargs = {}

CUSTOM_SYSTEM_PROMPT = "For the below pdf page, convert it into as accurate markdown format as possible with it's structure intact i.e, tables, charts, layouts etc. Return only the markdown with no explanation text. Do not exclude any content from the page."


MODEL = "gemini/gemini-1.5-pro"


@Client.on_message(filters.command("pdf2md", prefix) & filters.me)
async def pdf2md(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("Reply to a pdf file")
        return
    if not message.reply_to_message.document:
        await message.edit("Reply to a pdf file")
        return
    if not message.reply_to_message.document.mime_type == "application/pdf":
        await message.edit("Reply to a pdf file")
        return
    if gemini_key == "":
        await message.edit("Set GEMINI_KEY to use this command")
        return
    file_name = message.reply_to_message.document.file_name
    file_name = file_name.split(".")[0]
    if os.path.exists(f"{file_name}.md"):
        os.remove(f"{file_name}.md")
    md = f"{file_name}.md"
    os.environ["GEMINI_API_KEY"] = gemini_key
    await message.edit("Downloading pdf...")
    pdf = await message.reply_to_message.download()
    await message.edit("Converting pdf to markdown...")
    try:
        result = await zerox(
            file_path=pdf,
            model=MODEL,
            custom_system_prompt=CUSTOM_SYSTEM_PROMPT,
            select_pages=None,
            **kwargs,
        )
        if result:
            pages = result.pages
            for page in pages:
                with open(md, "a") as f:
                    f.write(page.content)
                    f.write("\n\n")
        else:
            await message.edit("No result")
            return
    except ModelAccessError:
        await message.edit("Model not accessible")
        return
    except NotAVisionModel:
        await message.edit("Model is not a vision model")
        return
    except litellm.InternalServerError:
        await message.edit("Internal Server Error")
        return
    except Exception as e:
        await message.edit(f"Error: {e}")
        return
    await message.edit("Uploading markdown...")
    await client.send_document(
        message.chat.id,
        document=md,
        file_name=f"{message.reply_to_message.document.file_name.split('.')[0]}.md",
        reply_to_message_id=message.reply_to_message.id,
    )
    await message.delete()
    os.remove(pdf)
    os.remove(md)


modules_help["pdf2md"] = {"pdf2md": "Convert a pdf to markdown"}
