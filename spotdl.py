import asyncio

import ffmpeg
from pyrogram import Client, filters, enums
from pyrogram.types import Message
import re

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import import_library, format_exc
from subprocess import STDOUT, check_call, CalledProcessError
import shutil
import os


_spotdl = import_library("spotdl")


if shutil.which("ffmpeg"):
    ffmpeg = True
else:
    ffmpeg = False


# noinspection PyUnusedLocal
@Client.on_message(filters.command(["spotdl", "sdl"], prefix) & filters.me)
async def spotdl_handler(client: Client, message: Message):
    try:
        if len(message.command) == 1 and not message.reply_to_message:
            await message.edit(
                "<b>Please use:</b> <code>.spotdl [link]</code>",
                parse_mode=enums.ParseMode.HTML,
            )
            return
        elif len(message.command) > 1:
            spoti_query = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
            spoti_query = message.reply_to_message.text.split("\n")[0]

        if not ffmpeg:
            return await message.edit(
                "<b>Please install (ffmpeg.org) library on your os (and restart Moon-Userbot)</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
            )

        await message.edit("<b>Downloading...</b>", parse_mode=enums.ParseMode.HTML)

        try:
            check_call(
                ["spotdl", "--output", "downloads/", f"{spoti_query}"],
                stdout=open("spotdl_logs.txt", "wb"),
            )
            logs = open("spotdl_logs.txt", "r", encoding="utf-8").read()
        except CalledProcessError:
            logs = "".join(
                open("spotdl_logs.txt", "r", encoding="utf-8").readlines()[-3:]
            )
            if "Skipping" in logs:
                name = logs.split("Skipping ")[1].split(" (file already exists)")[0]
            elif "Downloaded" in logs:
                name = logs.split('Downloaded "')[1].split('"')[0]

                await message.reply_audio(
                    f"downloads/{name}.mp3",
                    caption=f"<b>{name}</b>\n" f"<code>{spoti_query}</code>",
                )
                os.remove(f"downloads/{name}.mp3")
                return await message.delete()
            else:
                return await message.edit(
                    f"<b>Spotify-Download error:</b>\n<code>{logs}</code>",
                )

        if "Skipping" in logs:
            name = logs.split("Skipping ")[1].split(" (file already exists)")[0]
        else:
            name = logs.split('Downloaded "')[1].split('"')[0]

        await message.reply_audio(
            f"downloads/{name}.mp3",
            caption=f"<b>{name}</b>\n" f"<code>{spoti_query}</code>",
        )
        os.remove(f"downloads/{name}.mp3")
        await asyncio.sleep(0.5)
        return await message.delete()
    except Exception as e:
        return await message.edit(
            f"<b>Spotify-Download error:</b>\n{format_exc(e)}",
            parse_mode=enums.ParseMode.HTML,
        )


modules_help["spotdl"] = {
    "spotdl [link]*": "Download spotify music by link",
}
