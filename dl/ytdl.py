import json
import aiohttp
import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix


async def fetch_youtube_data(query, status_message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://apis.davidcyriltech.my.id/song?query={query}") as response:
                result = await response.json()

        if not result.get("status") or not result.get("result"):
            raise ValueError("No results found")

        return result["result"]
    except Exception as e:
        await status_message.edit_text(f"<code>Failed to fetch data: {str(e)}</code>")
        return None


async def download_file(url, file_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(file_name, "wb") as file:
                while chunk := await response.content.read(1024):
                    file.write(chunk)


@Client.on_message(filters.command(["yta", "ytaudio"], prefix) & filters.me)
async def youtube_audio_download(client: Client, message: Message):
    is_self = message.from_user and message.from_user.is_self
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else getattr(message.reply_to_message, "text", "").strip()
    )

    if not query:
        response = f"<b>Usage:</b> <code>{prefix}ytdla [query]</code>"
        await (message.edit(response) if is_self else message.reply(response))
        return

    status_message = await (
        message.edit_text(f"<code>Searching for {query} on YouTube...</code>")
        if is_self
        else message.reply(f"<code>Searching for {query} on YouTube...</code>")
    )

    youtube_data = await fetch_youtube_data(query, status_message)
    if not youtube_data:
        return

    title = youtube_data["title"]
    audio_url = youtube_data["audio"]["download_url"]
    audio_format = youtube_data["audio"]["format"]
    audio_quality = youtube_data["audio"]["quality"]

    await status_message.edit_text(f"<code>Downloading audio: {title}...</code>")
    file_name = f"{title}.{audio_format.lower()}"

    try:
        await download_file(audio_url, file_name)

        await client.send_audio(
            message.chat.id,
            file_name,
            caption=f"<b>Title:</b> {title}\n<b>Format:</b> {audio_format}\n<b>Quality:</b> {audio_quality}",
        )
    except Exception as e:
        await status_message.edit_text(f"<code>Failed to download audio: {str(e)}</code>")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

    await status_message.delete()


@Client.on_message(filters.command(["ytv", "ytvideo"], prefix) & filters.me)
async def youtube_video_download(client: Client, message: Message):
    is_self = message.from_user and message.from_user.is_self
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else getattr(message.reply_to_message, "text", "").strip()
    )

    if not query:
        response = f"<b>Usage:</b> <code>{prefix}ytdlv [query]</code>"
        await (message.edit(response) if is_self else message.reply(response))
        return

    status_message = await (
        message.edit_text(f"<code>Searching for {query} on YouTube...</code>")
        if is_self
        else message.reply(f"<code>Searching for {query} on YouTube...</code>")
    )

    youtube_data = await fetch_youtube_data(query, status_message)
    if not youtube_data:
        return

    title = youtube_data["title"]
    video_url = youtube_data["video"]["download_url"]
    video_format = youtube_data["video"]["format"]
    video_quality = youtube_data["video"]["quality"]

    await status_message.edit_text(f"<code>Downloading video: {title}...</code>")
    file_name = f"{title}.{video_format.lower()}"

    try:
        await download_file(video_url, file_name)

        await client.send_video(
            message.chat.id,
            file_name,
            caption=f"<b>Title:</b> {title}\n<b>Format:</b> {video_format}\n<b>Quality:</b> {video_quality}",
        )
    except Exception as e:
        await status_message.edit_text(f"<code>Failed to download video: {str(e)}</code>")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

    await status_message.delete()


modules_help["youtube"] = {
    "yta [query]": "search and download audio from YouTube",
    "ytv [query]": "search and download video from YouTube",
}
