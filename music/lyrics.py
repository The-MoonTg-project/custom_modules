import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

API_URL = "https://api.deline.web.id/tools/lyrics?title="

def format_duration(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"

def format_message(song: dict) -> str:
    info = (
        f"> **Song Info:**\n"
        f"> **Title:** {song.get('trackName') or song.get('name', 'Unknown')}\n"
        f"> **Artist:** {song.get('artistName', 'Unknown')}\n"
        f"> **Album:** {song.get('albumName', 'Unknown')}\n"
        f"> **Duration:** {format_duration(int(song.get('duration', 0)))}\n"
        f"> **Instrumental:** {'Yes' if song.get('instrumental') else 'No'}"
    )
    lyrics = "> **Lyrics:**\n> " + song.get("plainLyrics", "No lyrics available.").replace("\n", "\n> ")
    return f"{info}\n\n{lyrics}"

async def search_lyrics(message: Message, query: str):
    await message.edit(f"Searching lyrics for: {query}")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}{query}", timeout=10) as resp:
            if resp.status != 200:
                return await message.edit("API error occurred.")
            data = await resp.json()
            if not data.get("status") or not data.get("result"):
                return await message.edit("No lyrics found.")
            
            full_message = format_message(data["result"][0])

            if len(full_message) > 4096:
                chunks = [full_message[i:i+4096] for i in range(0, len(full_message), 4096)]
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await message.edit(chunk, parse_mode=enums.ParseMode.MARKDOWN)
                    else:
                        await message.reply(chunk, parse_mode=enums.ParseMode.MARKDOWN)
            else:
                await message.edit(full_message, parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.command(["lyrics"], prefix) & filters.me)
async def lyrics_search(client, message: Message):
    query = (
        message.text.split(maxsplit=1)[1].strip()
        if len(message.command) > 1 else
        message.reply_to_message.text.strip() if message.reply_to_message and message.reply_to_message.text else None
    )
    if not query:
        return await message.edit("Usage: lyrics <song name>")
    
    await search_lyrics(message, query)

modules_help["lyrics"] = {
    "lyrics [song name]*": "Get song info and lyrics in two separate quotes inside a single message"
}
