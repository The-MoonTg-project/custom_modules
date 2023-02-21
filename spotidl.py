import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
import re

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import import_library, format_exc
from subprocess import STDOUT, check_call, CalledProcessError
import os


_spotdl = import_library("spotdl")


try:
    check_call(
        ["apt-get", "install", "-y", "ffmpeg"],
        stdout=open(os.devnull, "wb"),
        stderr=STDOUT,
    )
    ffmpeg = True
except:
    ffmpeg = False


# noinspection PyUnusedLocal
@Client.on_message(filters.command(["spotdl", "sdl"], prefix) & filters.me)
async def spotdl_handler(client: Client, message: Message):
    try:
        if len(message.command) == 1 and not message.reply_to_message:
            await message.edit("<b>Please use:</b> <code>.spotdl [link]</code>")
            return
        elif len(message.command) > 1:
            spoti_query = message.command[1]
        elif message.reply_to_message:
            spoti_query = message.reply_to_message.text.split('\n')[0]

        if not ffmpeg:
            return await message.edit(
                "<b>Please install (ffmpeg.org) library on your os (and restart Dragon-Userbot)</b>",
                disable_web_page_preview=True,
            )

        await message.edit("<b>Downloading...</b>")

        try:
            download = check_call(
                ["spotdl", "--output", "downloads/", f'"{spoti_query}"'],
                stdout=open("spotdl_logs.txt", "wb"),
            )
            logs = open("spotdl_logs.txt", "r", encoding="utf-8").read()
        except CalledProcessError:
            logs = "".join(open("spotdl_logs.txt", "r", encoding="utf-8").readlines()[-3:])
            if " as it's already downloaded" in logs:
                name = logs.split("\" as it's already downloaded")[0].split('"')[-1]
                await message.reply_audio(
                    f"downloads/{name}.mp3",
                    caption=f"<b>{name}</b>\n" f"<code>{spoti_query}</code>",
                )
                os.remove(f"downloads/{name}.mp3")
                return await message.delete()
            else:
                return await message.edit(
                    f"<b>Spotify-Download error:</b>\n<code>{logs}</code>"
                )

        music_names = re.findall(r"(?<= for \")[^\"]+", logs)

        for name in set(music_names):
            await message.reply_audio(
                f"downloads/{name}.mp3",
                caption=f"<b>{name}</b>\n" f"<code>{spoti_query}</code>",
            )
            os.remove(f"downloads/{name}.mp3")
            await asyncio.sleep(0.5)
        return await message.delete()
    except Exception as e:
        await message.edit(f"<b>Spotify-Download error:</b>\n{format_exc(e)}")


modules_help["spotdl"] = {
    "spotdl [link]*": "Download spotify music by link",
}
