import os
import time
from io import BytesIO

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.scripts import import_library

yt_dlp = import_library("yt_dlp", "yt-dlp")

from urllib.parse import parse_qs, urlparse

from utils.scripts import format_exc, progress, resize_image
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError

from utils import modules_help, prefix

ydv_opts = {
    "format": "bv[ext=mp4]+ba/bv*+ba/b[ext=mp4]/b",
    "geo_bypass": True,
    "nocheckcertificate": True,
    "addmetadata": True,
    "noplaylist": True,
    "outtmpl": "downloads/ytdl/videos/%(id)s.%(ext)s",
}

ydm_opts = {
    "format": "bestaudio/best",
    "default_search": "ytsearch",
    "geo_bypass": True,
    "nocheckcertificate": True,
    "addmetadata": True,
    "noplaylist": True,
    "outtmpl": "downloads/ytdl/audios/%(title)s.%(ext)s",
}

API_URL = "https://apis.davidcyriltech.my.id/"


def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        video_id = parsed_url.path[1:]
    else:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]
    return video_id


async def search_api(query, is_videoId=False, video=False):
    query = str(query)
    async with aiohttp.ClientSession() as session:
        if is_videoId:
            async with session.get(
                f"{API_URL}download/{'ytmp4' if video else 'ytmp3'}?url=https://youtube.com/watch?v="
                + query
            ) as resp:
                data = await resp.json()
            if data["success"]:
                title = data["result"]["title"]
                thumb_url = data["result"]["thumbnail"]
                link = data["result"]["download_url"]
                return title, thumb_url, link
        else:
            async with session.get(f"{API_URL}song?query=" + query) as resp:
                data = await resp.json()
            if data["status"]:
                result = data["result"]
                if result:
                    title = result["title"]
                    thumb_url = result["thumbnail"]
                    link = (
                        result["video"]["download_url"]
                        if video
                        else result["audio"]["download_url"]
                    )
                    return title, thumb_url, link
    return None, None, None


async def download_thumb(thumb_url):
    if not thumb_url:
        return None
    async with aiohttp.ClientSession() as session:
        async with session.get(thumb_url) as resp:
            with open("thumbyt.jpg", "wb") as f:
                f.write(await resp.read())
    return resize_image("thumbyt.jpg")


async def download_file(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(path, "wb") as f:
                f.write(await resp.read())


async def download_video(url):
    try:
        with YoutubeDL(ydv_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            i_d = info.get("id")
            title = info.get("title")
            ext = info.get("ext")
            thumb_url = info.get("thumbnail")
            img = await download_thumb(thumb_url)
            file_path = f"downloads/ytdl/videos/{i_d}.{ext}"
            ydl.download([url])
            return file_path, title, img, thumb_url
    except (DownloadError, ExtractorError):
        video_id = extract_video_id(url)
        is_videoId = True if video_id is not None else False
        video_id = url if video_id is None else video_id
        title, thumb_url, songlink = await search_api(video_id, is_videoId, True)
        img = await download_thumb(thumb_url)
        os.makedirs("downloads/ytdl/videos", exist_ok=True)
        await download_file(songlink, "downloads/ytdl/videos/" + title + ".mp4")
        return "downloads/ytdl/videos/" + title + ".mp4", title, img, thumb_url


async def download_music(url):
    try:
        with YoutubeDL(ydm_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            thumb_url = info.get("thumbnail")
            img = await download_thumb(thumb_url)
            ydl.download([url])
            # Search for the file in the audios folder
            for file in os.listdir("downloads/ytdl/audios"):
                file_path = os.path.join("downloads/ytdl/audios", file)
                title = os.path.splitext(file)[0]
                if os.path.isfile(file_path):
                    break
            else:
                raise FileNotFoundError("Downloaded file not found in audios folder")
            return file_path, title, img
    except (DownloadError, ExtractorError):
        video_id = extract_video_id(url)
        is_videoId = True if video_id is not None else False
        video_id = url if video_id is None else video_id
        title, thumb_url, songlink = await search_api(video_id, is_videoId)
        img = await download_thumb(thumb_url)
        os.makedirs("downloads/ytdl/audios", exist_ok=True)
        await download_file(songlink, "downloads/ytdl/audios/" + title + ".mp3")
        return "downloads/ytdl/audios/" + title + ".mp3", title, img


@Client.on_message(filters.command(["ytv", "ytm"], prefix) & filters.me)
async def ytvm(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a YouTube URL to download.")

    if message.command[0] == "ytv":
        await message.edit_text("Starting Download...")
        try:
            url = message.text.split(maxsplit=1)[1]
            file_path, title, img, thumb_url = await download_video(url)

            new_path = file_path.replace(".webm", ".mp4")
            os.rename(file_path, new_path)
            file_path = new_path

            ms = await message.edit_text("Uploading Video...")
            c = time.time()

            cover = None
            if thumb_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumb_url) as resp:
                        cover = BytesIO(await resp.read())

            await client.send_video(
                message.chat.id,
                video=file_path,
                thumb=img,
                cover=cover,
                caption=f"<code>{title}</code>",
                progress=progress,
                progress_args=(ms, c, "<code>Uploading Video...</code>"),
            )
            os.remove(file_path)
            os.remove("thumbyt.jpg")
            await message.delete()
        except Exception as e:
            await message.edit_text(f"An error occurred: {format_exc(e)}")
    elif message.command[0] == "ytm":
        await message.edit_text("Starting Download...")
        try:
            url = message.text.split(None, 1)[1]
            file_path, title, img = await download_music(url)

            new_path = file_path.replace(".webm", ".m4a")
            os.rename(file_path, new_path)
            file_path = new_path

            ms = await message.edit_text("Uploading Audio...")
            c = time.time()

            await client.send_audio(
                message.chat.id,
                audio=file_path,
                thumb=img,
                caption=f"<code>{title}</code>",
                progress=progress,
                progress_args=(ms, c, "<code>Uploading Audio...</code>"),
            )
            os.remove(file_path)
            os.remove("thumbyt.jpg") if os.path.exists("thumbyt.jpg") else None
            await message.delete()
        except Exception as e:
            await message.edit_text(f"An error occurred: {format_exc(e)}")
    else:
        return await message.edit_text("Oh Damn Lol")


modules_help["ytdl"] = {
    "ytv [name|link]*": "Download Video From YouTube",
    "ytm [name|link]*": "Download Music From YouTube",
}
