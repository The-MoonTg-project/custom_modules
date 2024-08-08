import os
import time
import requests

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.scripts import import_library
yt_dlp = import_library('yt_dlp', 'yt-dlp')
from yt_dlp import YoutubeDL

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, progress, resize_image

ydv_opts = {
    'format': 'best',
    "geo_bypass": True,
    "nocheckcertificate": True,
    "addmetadata": True,
    "noplaylist": True,
    'outtmpl': 'videos/%(id)s.%(ext)s'
}
ydm_opts = {
    'format': 'm4a',
    "geo_bypass": True,
    "preferredquality": "320",
    "nocheckcertificate": True,
    "addmetadata": True,
    "noplaylist": True,
    'outtmpl': 'audios/%(id)s.%(ext)s',
}

def download_video(url):
    with YoutubeDL(ydv_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        i_d = info.get('id')
        title = info.get('title')
        ext = info.get('ext')
        thumb_url = info.get('thumbnail')
        print(thumb_url)
        if thumb_url:
            resp = requests.get(thumb_url)
            img_content = resp.content
            with open("thumbyt.jpg", 'wb') as f:
                f.write(img_content)
            img = resize_image("thumbyt.jpg")
        file_path = f"videos/{i_d}.{ext}"
        ydl.download([url])
        return file_path, title, img

def download_music(url):
    with YoutubeDL(ydm_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        i_d = info.get('id')
        title = info.get('title')
        thumb_url = info.get('thumbnail')
        if thumb_url:
            resp = requests.get(thumb_url)
            with open("thumbyt.jpg", 'wb') as f:
                f.write(resp.content)
            img = resize_image("thumbyt.jpg")
        file_path = f"audios/{i_d}.m4a"
        ydl.download([url])
        return file_path, title, img

@Client.on_message(filters.command(['ytv', 'ytm'], prefix) & filters.me)
async def upload_video(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text('Please provide a YouTube URL to download.')

    if message.command[0] == 'ytv':
        await message.edit_text("Starting Download...")
        try:
            url = message.text.split(maxsplit=1)[1]
            # await message.edit_text("Starting Download...")
            file_path, title, img = download_video(url)

            ms = await message.edit_text("Uploading Video...")
            c = time.time()

            await client.send_video(message.chat.id, video=file_path, thumb=img, caption=f"<code>{title}<code/>", progress=progress, progress_args=(ms, c, '`Uploading Video...`'))
            os.remove(file_path)
            os.remove("thumbyt.jpg")
            await message.delete()
        except Exception as e:
            await message.edit_text(f"An error occurred: {format_exc(e)}")
    elif message.command[0] == 'ytm':
        await message.edit_text("Starting Download...")
        try:
            url = message.text.split(None, 1)[1]
            file_path, title, img = download_music(url)

            os.rename(file_path, f"audios/{title}.m4a")

            ms = await message.edit_text("Uploading Audio...")
            c = time.time()

            await client.send_audio(message.chat.id, audio=f"audios/{title}.m4a", thumb=img, caption=f"<code>{title}<code/>", progress=progress, progress_args=(ms, c, '`Uploading Audio...`'))
            os.remove(f"audios/{title}.m4a")
            os.remove("thumbyt.jpg")
            await message.delete()
        except Exception as e:
            await message.edit_text(f"An error occurred: {format_exc(e)}")
    else:
        return await message.edit_text("Oh Damn Lol")
        
modules_help["ytdl"] = {
    "ytv [link]*": "Download Video From YouTube",
    "ytm [link]*": "Download Music From YouTube",
}
