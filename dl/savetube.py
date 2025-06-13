import aiohttp
import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

SEARCH_API = "https://api.nekorinn.my.id/search/youtube?q={}"
DL_API = "https://api.nekorinn.my.id/downloader/savetube?url={}&format={}"
YOUTUBE_LINK_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)[\w\-]{11,}')

async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def download_file(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(path, "wb") as f:
                while chunk := await resp.content.read(1024):
                    f.write(chunk)

def extract_youtube_link(text):
    match = YOUTUBE_LINK_REGEX.search(text)
    if match:
        url = match.group(0)
        return url if url.startswith("http") else "https://" + url
    return None

def safe_filename(title, ext):
    name = "".join(x for x in title if x.isalnum() or x in "._- ").strip() or "youtube_file"
    return f"{name}.{ext}"

async def resolve_input(message, cmd):
    is_self = message.from_user and message.from_user.is_self
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else getattr(message.reply_to_message, "text", "").strip()
    )
    if not query:
        txt = f"<b>Usage:</b> <code>{prefix}{cmd} [query or YouTube link]</code>"
        await (message.edit(txt) if is_self else message.reply(txt))
        return None, None, None
    url = extract_youtube_link(query)
    if url:
        status = await (message.edit_text("<code>Downloading from YouTube link...</code>") if is_self else message.reply("<code>Downloading from YouTube link...</code>"))
        return {"title": "YouTube Video", "url": url}, status, True
    status = await (message.edit_text(f"<code>Searching for {query} on YouTube...</code>") if is_self else message.reply(f"<code>Searching for {query} on YouTube...</code>"))
    data = await fetch_json(SEARCH_API.format(query))
    if not data.get("status") or not data.get("result"):
        await status.edit_text("<code>No search results found.</code>")
        return None, None, None
    return data["result"][0], status, False

async def process_download(client, message, status, video, fmt, send_type):
    title, vurl = video["title"], video["url"]
    dl_info = await fetch_json(DL_API.format(vurl, fmt))
    if not dl_info.get("status") or not dl_info.get("result"):
        await status.edit_text("<code>Download API did not return results.</code>")
        return
    result = dl_info["result"]
    durl = result["download"]
    ext = "mp3" if fmt == "mp3" else "mp4"
    fname = safe_filename(title, ext)
    thumb = result.get("cover")
    thumb_path = None
    if thumb:
        thumb_path = safe_filename(title, "jpg")
        await download_file(thumb, thumb_path)
    try:
        await status.edit_text(f"<code>Downloading {'audio' if fmt == 'mp3' else 'video'}: {title} ({fmt})...</code>")
        await download_file(durl, fname)
        caption = f"<b>Title:</b> {result.get('title', title)}\n<b>Format:</b> {result.get('format', fmt)}"
        send = client.send_audio if send_type == "audio" else client.send_video
        await send(
            message.chat.id,
            fname,
            caption=caption,
            thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
        )
    except Exception as e:
        await status.edit_text(f"<code>Failed to download: {str(e)}</code>")
    finally:
        if os.path.exists(fname): os.remove(fname)
        if thumb_path and os.path.exists(thumb_path): os.remove(thumb_path)
    await status.delete()

@Client.on_message(filters.command(["sta"], prefix))
async def yta(client: Client, message: Message):
    video, status, _ = await resolve_input(message, "yta")
    if video: await process_download(client, message, status, video, "mp3", "audio")

@Client.on_message(filters.command(["stv"], prefix))
async def ytv(client: Client, message: Message):
    video, status, _ = await resolve_input(message, "ytv")
    if video: await process_download(client, message, status, video, "720", "video")

@Client.on_message(filters.command(["stvl"], prefix))
async def ytvl(client: Client, message: Message):
    video, status, _ = await resolve_input(message, "ytvl")
    if video: await process_download(client, message, status, video, "360", "video")

modules_help["savetube"] = {
    "sta [query or YouTube link]": "Download audio (mp3) from YouTube or a direct YouTube link.",
    "stv [query or YouTube link]": "Download high quality video (720p) from YouTube or a direct YouTube link.",
    "stvl [query or YouTube link]": "Download low quality video (360p) from YouTube or a direct YouTube link.",
}
