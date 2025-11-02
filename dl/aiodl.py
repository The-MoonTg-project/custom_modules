import os
import re
import time
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import progress

API_URL = "https://api.deline.web.id/downloader/aio?url="

def sanitize_title(title: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip()[:50]

@Client.on_message(filters.command("aio", prefix))
async def aio_video(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) > 1:
        video_url = message.text.split(maxsplit=1)[1].strip()
    elif message.reply_to_message:
        video_url = message.reply_to_message.text.strip()
    else:
        usage = f"<b>Usage:</b> <code>{prefix}aio [video link]</code>"
        if message.from_user.id == (await client.get_me()).id:
            await message.edit_text(usage)
        else:
            await message.reply_text(usage)
        return

    ms = await (message.edit_text if message.from_user.id == (await client.get_me()).id else message.reply_text)(
        "<code>Fetching video details...</code>"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{video_url}") as resp:
                if resp.status != 200:
                    await ms.edit_text("<code>API error: unable to fetch video.</code>")
                    return
                data = await resp.json()

            if not data.get("status"):
                await ms.edit_text("<code>No downloadable video found.</code>")
                return

            result = data.get("result", {})
            medias = result.get("medias", [])
            video_item = next(
                (m for m in medias if m["type"] == "video" and "no_watermark" in m.get("quality", "").lower()), None
            ) or next((m for m in medias if m["type"] == "video"), None)

            if not video_item:
                await ms.edit_text("<code>No downloadable video found.</code>")
                return

            video_link = video_item["url"]
            title = sanitize_title(result.get("title", "video"))
            video_file = f"{title}.mp4"

            await ms.edit_text("<code>Downloading video...</code>")
            async with session.get(video_link) as vid:
                if vid.status != 200:
                    await ms.edit_text("<code>Download failed.</code>")
                    return
                with open(video_file, "wb") as f:
                    while chunk := await vid.content.read(1024):
                        f.write(chunk)

        c_time = time.time()
        await ms.edit_text("<code>Uploading video...</code>")
        await client.send_video(
            chat_id,
            video=video_file,
            caption=f"<b>Title:</b> {title}\n<b>Quality:</b> High",
            progress=progress,
            progress_args=(ms, c_time, "<code>Uploading video...</code>"),
        )

        await ms.delete()
        if os.path.exists(video_file):
            os.remove(video_file)

    except Exception as e:
        await ms.edit_text(f"<code>Error:</code> {str(e)}")

@Client.on_message(filters.command("aioa", prefix))
async def aio_audio(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) > 1:
        video_url = message.text.split(maxsplit=1)[1].strip()
    elif message.reply_to_message:
        video_url = message.reply_to_message.text.strip()
    else:
        usage = f"<b>Usage:</b> <code>{prefix}aioa [video link]</code>"
        if message.from_user.id == (await client.get_me()).id:
            await message.edit_text(usage)
        else:
            await message.reply_text(usage)
        return

    ms = await (message.edit_text if message.from_user.id == (await client.get_me()).id else message.reply_text)(
        "<code>Fetching audio details...</code>"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{video_url}") as resp:
                if resp.status != 200:
                    await ms.edit_text("<code>API error: unable to fetch audio.</code>")
                    return
                data = await resp.json()

            if not data.get("status"):
                await ms.edit_text("<code>No downloadable audio found.</code>")
                return

            result = data.get("result", {})
            medias = result.get("medias", [])
            audio_item = next((m for m in medias if m["type"] == "audio"), None)

            if not audio_item:
                await ms.edit_text("<code>No downloadable audio found.</code>")
                return

            audio_link = audio_item["url"]
            title = sanitize_title(result.get("title", "audio"))
            audio_file = f"{title}.mp3"

            await ms.edit_text("<code>Downloading audio...</code>")
            async with session.get(audio_link) as aud:
                if aud.status != 200:
                    await ms.edit_text("<code>Download failed.</code>")
                    return
                with open(audio_file, "wb") as f:
                    while chunk := await aud.content.read(1024):
                        f.write(chunk)

        c_time = time.time()
        await ms.edit_text("<code>Uploading audio...</code>")
        await client.send_audio(
            chat_id,
            audio=audio_file,
            caption=f"<b>Title:</b> {title}\n<b>Type:</b> Audio",
            progress=progress,
            progress_args=(ms, c_time, "<code>Uploading audio...</code>"),
        )

        await ms.delete()
        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        await ms.edit_text(f"<code>Error:</code> {str(e)}")

modules_help["aiodl"] = {
    "aio [video link]": "Download high-quality video from the provided link",
    "aioa [video link]": "Download audio from the provided link",
}
