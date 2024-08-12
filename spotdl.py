import asyncio
import os
import shutil
import time
import requests
from pytubefix import YouTube

from subprocess import check_call, CalledProcessError
from urllib.parse import parse_qs, urlparse

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_module_help, import_library, format_exc, progress

spotdl = import_library("spotdl")

exiftool = import_library("exiftool", "pyexiftool")
from exiftool import ExifToolHelper


def get_thumb(file_name):
    with ExifToolHelper() as et:
        yt_link = et.get_metadata(file_name)[0]["ID3:Comment-xxx"]
        yt = YouTube(yt_link)
        thumb = yt.thumbnail_url
        with open(f"{file_name}.jpg", "wb") as f:
            f.write(requests.get(thumb).content)
    return f"{file_name}.jpg"


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

        m = await message.edit("<b>Downloading...</b>", parse_mode=enums.ParseMode.HTML)

        if not shutil.which("ffmpeg") or message.command[0] == "sdl":
            url = "https://spotify-mp3-downloader.vercel.app/get_download_link?search="
            search_query = spoti_query.replace(" ", "%20")
            response = requests.get(url + search_query)
            if response.status_code == 200:
                download_link = response.json()["download_link"]
                song_name = get_song_name(download_link)
                await message.reply_audio(download_link, caption=f"<b>{song_name}</b>")
                await asyncio.sleep(0.5)
                await m.delete()
                return
            else:
                await m.edit("api request was unsuccessful.")
                return

        try:
            check_call(
                ["spotdl", "--output", "spotdl/", f"{spoti_query}"],
                stdout=open("spotdl_logs.txt", "wb"),
            )
            logs = "".join(
                open("spotdl_logs.txt", "r", encoding="utf-8").readlines()[-3:]
            )
        except CalledProcessError:
            logs = "".join(
                open("spotdl_logs.txt", "r", encoding="utf-8").readlines()[-3:]
            )
        ct = time.time()
        if "Skipping" or "Downloaded" in logs:
            for filename in os.listdir("spotdl/"):
                if filename.endswith(".mp3"):
                    try:
                        check_call("exiftool", f"shutil/{filename}")
                        thumb = get_thumb(filename) 
                    except CalledProcessError:
                        thumb = None
                    await message.reply_audio(
                        audio=f"spotdl/{filename}",
                        caption=f"<b>{os.path.splitext(filename)[0]}</b>",
                        thumb=thumb,
                        progress=progress,
                        progress_args=(m, ct, f"Uploading {filename}..."),
                        reply_to_message_id=(
                            message.reply_to_message.id
                            if message.reply_to_message
                            else None
                        ),
                    )
                    if os.path.exists(thumb):
                        os.remove(thumb)
                    if os.path.exists("spotdl/" + filename):
                        os.remove("spotdl/" + filename)
        else:
            await m.edit(logs)
        if os.path.exists("spotdl_logs.txt"):
            os.remove("spotdl_logs.txt")
        await asyncio.sleep(0.5)
        await m.delete()

    except Exception as e:
        await m.edit(f"<b>Spotify-Download error:</b>\n{format_exc(e)}")


modules_help["spotdl"] = {
    "spotdl [link/query]*": "Download spotify music by link",
    "sdl [query]*": "Download spotify music through api",
}
