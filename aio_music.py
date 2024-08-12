import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

def format_spotify_result(data):
    result = ""
    for item in data[:15]:  # Limit to 15 results
        result += f"🎵 **{item['title']}** by {item['artist']}\n"
        result += f"Album: {item['album']}\n"
        result += f"Duration: {item['duration']}\n"
        result += f"Popularity: {item['popularity']}\n"
        result += f"Publish Date: {item['publish']}\n"
        result += f"[Listen on Spotify]({item['url']})\n\n"
    return result

def format_lyrics_result(data):
    return f"🎵 **{data['fullTitle']}** by {data['artist']}\n\n{data['lyrics']}"

def format_soundcloud_result(data):
    result = ""
    for item in data[:15]:  # Limit to 15 results
        result += f"🎵 **{item['title']}**\n"
        result += f"Genre: {item['genre']}\n"
        result += f"Duration: {item['duration'] // 1000 // 60}:{item['duration'] // 1000 % 60}\n"
        result += f"Likes: {item['likes']}\n"
        result += f"Plays: {item['play']}\n"
        result += f"[Listen on SoundCloud]({item['link']})\n\n"
    return result

def format_deezer_result(data):
    result = ""
    for item in data[:15]:  # Limit to 15 results
        result += f"🎵 **{item['title']}** by {item['artist']}\n"
        result += f"Duration: {item['duration']}\n"
        result += f"Rank: {item['rank']}\n"
        result += f"[Listen on Deezer]({item['url']})\n\n"
    return result

def format_apple_music_result(data):
    result = ""
    for item in data[:15]:  # Limit to 15 results
        title = item.get('title', 'Unknown Title')
        artists = item.get('artists', 'Unknown Artist')
        music_type = item.get('type', 'Unknown Type')
        url = item.get('url', '#')
        
        result += f"🎵 **{title}** by {artists}\n"
        result += f"Type: {music_type}\n"
        result += f"[Listen on Apple Music]({url})\n\n"
    return result

async def search_music(api_url, format_function, message, query):
    await message.edit("Searching...")
    url = f"{api_url}{query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = response.json()  # Directly get the JSON data
            
            if isinstance(data, list):
                result = format_function(data)
            elif isinstance(data, dict) and "data" in data:
                result = format_function(data["data"])
            else:
                result = "No data found or unexpected format."

            await message.edit(result, parse_mode=enums.ParseMode.MARKDOWN)
        except (ValueError, KeyError, TypeError) as e:
            await message.edit(f"An error occurred while processing the data: {str(e)}")
    else:
        await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["spotify"], prefix) & filters.me)
async def spotify_search(client, message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else message.reply_to_message.text
    if not query:
        await message.edit("Usage: spotify <query>")
        return
    await search_music("https://deliriusapi-official.vercel.app/search/spotify?q=", format_spotify_result, message, query)

@Client.on_message(filters.command(["lyrics"], prefix) & filters.me)
async def lyrics_search(client, message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else message.reply_to_message.text
    if not query:
        await message.edit("Usage: lyrics <song name>")
        return
    await search_music("https://deliriusapi-official.vercel.app/search/letra?query=", format_lyrics_result, message, query)

@Client.on_message(filters.command(["soundcloud"], prefix) & filters.me)
async def soundcloud_search(client, message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else message.reply_to_message.text
    if not query:
        await message.edit("Usage: soundcloud <query>")
        return
    await search_music("https://deliriusapi-official.vercel.app/search/soundcloud?q=", format_soundcloud_result, message, query)

@Client.on_message(filters.command(["deezer"], prefix) & filters.me)
async def deezer_search(client, message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else message.reply_to_message.text
    if not query:
        await message.edit("Usage: deezer <query>")
        return
    await search_music("https://deliriusapi-official.vercel.app/search/deezer?q=", format_deezer_result, message, query)

@Client.on_message(filters.command(["applemusic"], prefix) & filters.me)
async def applemusic_search(client, message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else message.reply_to_message.text
    if not query:
        await message.edit("Usage: applemusic <query>")
        return
    await search_music("https://deliriusapi-official.vercel.app/search/applemusic?text=", format_apple_music_result, message, query)

modules_help["aio_music"] = {
    "spotify [query]*": "Search for songs on Spotify",
    "lyrics [song name]*": "Get the lyrics of a song",
    "soundcloud [query]*": "Search for songs on SoundCloud",
    "deezer [query]*": "Search for songs on Deezer",
    "applemusic [query]*": "Search for songs on Apple Music",
}
