from ytdl import modules_help
from song import thumb
from song import progress
from time import time
from os import os
from sys import prefix
import json
import requests



from pyrogram import Client, filters
from pyrogram.types import Message





@Client.on_message(filters.command(["svn", "saavn"], prefix) & filters.me)
async def saavn(client: Client, message: Message):
    thumb = "thumb.jpg"
    if not os.path.isfile(thumb):
        thumb = None
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
    response = requests.get(f"https://musicapi.x007.workers.dev/search?q={query}&searchEngine=seevn")

    result = json.loads(response.text)
    
    song_details = result['response'][0]
    song_id = song_details['id']
    song_name = song_details['title']

    await ms.edit_text(f"<code>Found: {song_name} </code>\n Downloading...")
    song = requests.get(f"https://musicapi.x007.workers.dev/fetch?id={song_id}")
    
    with open(f"{song_name}.mp3", "wb") as f:
        f.write(song.content)
    
    await ms.edit_text(f"<code>Uploading {song_name}... </code>")
    c_time = time.time()
    await client.send_document(chat_id, f"{song_name}.mp3", caption=f"Song Name: {song_name}", progress=progress, progress_args=(ms, c_time, f'`Uploading {song_name}...`'), thumb=thumb)
    await ms.delete()
    os.remove(f"{song_name}.mp3")
    
@Client.on_message(filters.command("wynk", prefix) & filters.me)
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
    response = requests.get(f"https://musicapi.x007.workers.dev/search?q={query}&searchEngine=seevn")

    result = json.loads(response.text)

    song_details = result['response'][0]
    song_id = song_details['id']
    song_name = song_details['title']

    await ms.edit_text(f"<code>Found: {song_name} </code>\n Downloading...")
    song = requests.get(f"https://musicapi.x007.workers.dev/fetch?id={song_id}")
    
    with open(f"{song_name}.mp3", "wb") as f:
        f.write(song.content)
    
    await ms.edit_text(f"<code>Uploading {song_name}... </code>")
    c_time = time.time()
    await client.send_document(chat_id, f"{song_name}.mp3", caption=f"Song Name: {song_name}", progress=progress, progress_args=(ms, c_time, f'`Uploading {song_name}...`'), thumb=thumb)
    await ms.delete()
    os.remove(f"{song_name}.mp3")


modules_help["song"] = {
    "svn": "search, download and upload songs from Saavn",
    "wynk": "search, download and upload songs from wynk",
}
