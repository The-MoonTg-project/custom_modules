import json
import os
from io import BytesIO

from pyrogram import Client, filters

# noinspection PyUnresolvedReferences
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# noinspection PyUnresolvedReferences
from utils.scripts import format_exc, import_library

aiohttp = import_library("aiohttp")
import urllib.parse


async def get_code(code: str):
    return urllib.parse.quote_plus(code)
    # return code.replace("\n", "%250A")


@Client.on_message(
    filters.command(["carbonnowsh", "carboon", "carbon", "cboon"], prefix) & filters.me
)
async def carbon_handler(_: Client, message: Message):
    try:
        filepath = None
        if (
            len(message.command) == 1
            and not message.reply_to_message
            and not message.document
        ):
            return await message.edit(
                "<b>Please reply to a message or send a code.</b>"
            )
        elif len(message.command) > 1:
            code = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
            if message.reply_to_message.document:
                filepath = f"downloads/{message.reply_to_message.document.file_name}"
                await message.reply_to_message.download(filepath)
                code = open(filepath, "r", encoding="utf-8").read()
            elif message.reply_to_message.text:
                code = message.reply_to_message.text
            elif message.reply_to_message.caption:
                code = message.reply_to_message.caption
            else:
                return await message.edit(
                    "<b>Please reply to a message or send a code.</b>"
                )
        elif message.document:
            filepath = f"downloads/{message.document.file_name}"
            await message.download(filepath)
            code = open(filepath, "r", encoding="utf-8").read()
        else:
            return await message.edit(
                "<b>Please reply to a message or send a code.</b>"
            )

        await message.edit("<b>Generating image...</b>")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://carbonnowsh.herokuapp.com/",
                json={"code": await get_code(code)},
            ) as resp:
                if not resp.ok:
                    return await message.edit("<b>Error while fetching the image.</b>")
                image = BytesIO(await resp.read())
                image.name = "carbon.jpg"
                image.seek(0)
        await message.reply_photo(image, caption=f"<b>Generated image:</b>")
        await message.delete()

        if filepath:
            os.remove(filepath)
    except Exception as e:
        return await message.edit(format_exc(e))


modules_help["carbon"] = {
    "carbon [code/file/reply]": "Create beautiful image with your code",
}
