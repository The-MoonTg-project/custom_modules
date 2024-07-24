import asyncio
import os
import shutil
from subprocess import STDOUT, check_call, CalledProcessError
from urllib.parse import parse_qs, urlparse

from click import command
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_module_help, import_library, format_exc
import requests

spotdl = import_library("spotdl")


def get_song_name(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    song_name = query_params.get("n", [""])[0].replace("%20", " ")
    return song_name


@Client.on_message(filters.command(["spotdl", "sdl"], prefix) & filters.me)
async def spotdl(_, message: Message):
    try:
        if not len(message.command) > 1 and not message.reply_to_message:
            await message.edit(
                format_module_help("spotdl"),
                parse_mode=enums.ParseMode.HTML,
            )
            return

        spoti_query = (
            message.text.split(maxsplit=1)[1]
            if len(message.command) > 1
            else message.reply_to_message.text.split("\n")[0]
        )

        await message.edit("<b>Downloading...</b>", parse_mode=enums.ParseMode.HTML)

        if not shutil.which("ffmpeg") or message.command[0] == "sdl":
            url = "https://spotify-mp3-downloader.vercel.app/get_download_link?search="
            search_query = spoti_query.replace(" ", "%20")
            response = requests.get(url + search_query)
            if response.status_code == 200:
                download_link = response.json()["download_link"]
                song_name = get_song_name(download_link)
                await message.reply_audio(download_link, caption=f"<b>{song_name}</b>")
                return
            else:
                await message.edit("api request was unsuccessful.")
                return

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
        else:
            await message.edit(
                f"<b>Spotify-Download error:</b>\n<code>{logs}</code>",
            )
            return
        try:
            await message.reply_audio(
                f"downloads/{name}.mp3",
                caption=f"<b>{name}</b>",
            )
        except (IndexError, ValueError):
            return await message.edit("Error: File not found")

        os.remove(f"downloads/{name}.mp3")

        await asyncio.sleep(0.5)
        await message.delete()

    except Exception as e:
        await message.edit(f"<b>Spotify-Download error:</b>\n{format_exc(e)}")


modules_help["spotdl"] = {
    "spotdl [link/query]*": "Download spotify music by link",
    "sdl [query]*": "Download spotify music through api",
}
