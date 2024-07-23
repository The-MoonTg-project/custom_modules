import json
import requests
import time
import os

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import progress

@Client.on_message(filters.command(["svn", "saavn"], prefix) & filters.me)
async def saavn(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}svn [song name to search & download|upload]</code>"
        )
        return
    ms = await message.edit_text(f"<code>Searching for {query} on saavn</code>")
    response = requests.get(f"https://jiosaavn-api-qw5y.onrender.com/api/search/songs?query={query}")

    result = json.loads(response.text)

    if result['success'] and result['data']['results']:
        song_details = result['data']['results'][0]
        song_name = song_details['name']
        thumb = song_details['image'][1]['url']
        song_url = song_details['downloadUrl'][-1]['url']

        await ms.edit_text(f"<code>Found: {song_name} </code>\n Downloading...")
        with open(f"{song_name}.jpg", "wb") as f:
            f.write(requests.get(thumb).content)

        song = requests.get(song_url)

        with open(f"{song_name}.mp3", "wb") as f:
            f.write(song.content)

        await ms.edit_text(f"<code>Uploading {song_name}... </code>")
        c_time = time.time()
        await client.send_audio(chat_id, f"{song_name}.mp3", caption=f"<b>Song Name:</b> {song_name}", progress=progress, progress_args=(ms, c_time, f'`Uploading {song_name}...`'), thumb=f"{song_name}.jpg")
        await ms.delete()
        if os.path.exists(f"{song_name}.jpg"):
            os.remove(f"{song_name}.jpg")
        if os.path.exists(f"{song_name}.mp3"):
            os.remove(f"{song_name}.mp3")
    else:
        await ms.edit_text(f"<code>No results found for {query}</code>")

modules_help["song"] = {
    "svn": "search, download and upload songs from Saavn",
}
