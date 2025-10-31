import json
import requests
import time
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import progress


@Client.on_message(filters.command("spotify", prefix))
async def spotify_download(client: Client, message: Message):
    is_self = message.from_user and message.from_user.is_self
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else getattr(message.reply_to_message, "text", "").strip()
    )

    if not query:
        response = f"<b>Usage:</b> <code>{prefix}sdl [song name]</code>"
        await (message.edit(response) if is_self else message.reply(response))
        return

    status_message = await (
        message.edit_text(f"<code>Searching for {query} on Spotify...</code>")
        if is_self
        else message.reply(f"<code>Searching for {query} on Spotify...</code>")
    )

    try:
        search_result = requests.get(
            f"https://delirius-apiofc.vercel.app/search/spotify?q={query}&limit=1"
        ).json()
        if not (search_result.get("status") and search_result.get("data")):
            raise ValueError("No results found")
    except Exception as e:
        await status_message.edit_text(f"<code>Failed to search: {str(e)}</code>")
        return

    song_details = search_result["data"][0]
    await status_message.edit_text(
        f"<code>Found: {song_details['title']} by {song_details['artist']}</code>\n<code>Fetching download link...</code>"
    )

    try:
        download_result = requests.get(
            f"https://delirius-apiofc.vercel.app/download/spotifydl?url={song_details['url']}"
        ).json()
        if not download_result.get("status"):
            raise ValueError("Failed to fetch download link")
    except Exception as e:
        await status_message.edit_text(f"<code>Failed to fetch link: {str(e)}</code>")
        return

    song_download_link = download_result["data"].get("url")
    if not song_download_link or not song_download_link.startswith("http"):
        await status_message.edit_text("<code>Song isn't available for download.</code>")
        return

    await status_message.edit_text(f"<code>Downloading {download_result['data']['title']}...</code>")

    try:
        thumb_path = f"{download_result['data']['title']}.jpg"
        if download_result["data"]["image"]:
            with open(thumb_path, "wb") as thumb_file:
                thumb_file.write(requests.get(download_result["data"]["image"]).content)

        song_path = f"{download_result['data']['title']}.mp3"
        song_response = requests.get(song_download_link)
        if "audio" not in song_response.headers.get("Content-Type", ""):
            raise ValueError("Invalid audio file")
        
        with open(song_path, "wb") as song_file:
            song_file.write(song_response.content)
    except Exception:
        await status_message.edit_text(f"<code>Failed to download: Song isn't available.</code>")
        return

    await status_message.edit_text(f"<code>Uploading {download_result['data']['title']}...</code>")

    try:
        c_time = time.time()
        await client.send_audio(
            message.chat.id,
            song_path,
            caption=f"<b>Song Name:</b> {download_result['data']['title']}\n<b>Artist:</b> {download_result['data']['author']}",
            progress=progress,
            progress_args=(status_message, c_time, f"<code>Uploading {download_result['data']['title']}...</code>"),
            thumb=thumb_path if os.path.exists(thumb_path) else None,
        )
    except Exception as e:
        await status_message.edit_text(f"<code>Failed to upload: {str(e)}</code>")
    finally:
        for file in [thumb_path, song_path]:
            if os.path.exists(file):
                os.remove(file)

    await status_message.delete()


modules_help["spotify"] = {
    "spotify [song name]": "search, download, and upload songs from Spotify"
  }
