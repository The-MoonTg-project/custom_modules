#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import requests
import asyncio
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from modules.url import generate_screenshot

# API URLs
BASE_URL = "https://deliriussapi-oficial.vercel.app/"
URL = f"{BASE_URL}/ia"
GOOGLE_SEARCH_URL = f"{BASE_URL}/search/googlesearch?query="
YOUTUBE_SEARCH_URL = f"{BASE_URL}/search/ytsearch?q="
MOVIE_SEARCH_URL = f"{BASE_URL}/search/movie?query="
APK_SEARCH_URL = f"https://bk9.fun/search/apkfab?q="
APK_DOWNLOAD_URL = "https://bk9.fun/download/apkfab?url="


def clean_data(data):
    parts = data.split("$@$")

    if len(parts) > 1:
        return parts[-1]
    else:
        return data


# Store search results temporarily
search_results = {}


# Helper Functions
def format_google_results(results):
    results = results[:15]
    return results, "\n\n".join(
        [
            f"{i+1}. **[{item['title']}]({item['url']})**\n{item['description']}"
            for i, item in enumerate(results)
        ]
    )


def format_youtube_results(results):
    results = results[:15]
    return results, "\n\n".join(
        [
            f"{i+1}. **[{item['title']}]({item['url']})**\nPublished by: [{item['author']['name']}]({item['author']['url']}) - {item['views']} views - {item['duration']}"
            for i, item in enumerate(results)
        ]
    )


def format_movie_results(results):
    results = results[:15]
    return results, "\n\n".join(
        [
            f"{i+1}. **{item['title']}** ({item['release_date']})\nRating: {item['vote_average']}/10\nVotes: {item['vote_count']}"
            for i, item in enumerate(results)
        ]
    )


def format_apk_results(results):
    results = results[:15]
    return results, "\n\n".join(
        [f"{i+1}. [{item['title']}]({item['link']})" for i, item in enumerate(results)]
    )


async def send_screenshot(client, message, url):
    screenshot_data = generate_screenshot(url)
    if screenshot_data:
        await client.send_photo(
            message.chat.id,
            screenshot_data,
            caption=f"Screenshot of <code>{url}</code>",
            reply_to_message_id=message.id,
        )
    else:
        await message.reply("Failed to take screenshot.")


async def delete_search_data(client, chat_id, message_id):
    await asyncio.sleep(60)
    for key in ["google", "youtube", "movie", "apk"]:
        search_key = f"{chat_id}_{key}"
        if (
            search_key in search_results
            and search_results[search_key]["message_id"] == message_id
        ):
            del search_results[search_key]
            try:
                await client.delete_messages(chat_id, message_id)
            except:
                pass
            break


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
        title = item.get("title", "Unknown Title")
        artists = item.get("artists", "Unknown Artist")
        music_type = item.get("type", "Unknown Type")
        url = item.get("url", "#")
        result += f"🎵 **{title}** by {artists}\n"
        result += f"Type: {music_type}\n"
        result += f"[Listen on Apple Music]({url})\n\n"
    return result


async def search_music(api_url, format_function, message, query):
    await message.edit("Searching...")
    url = f"{api_url}{query}&limit=10"
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
    elif response.json()["msg"]:
        await message.edit(response.json()["msg"])
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["gsearch"], prefix) & filters.me)
async def google_search(client: Client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    elif len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    else:
        return await message.edit_text(f"{prefix}gsearch <query/reply to query>")

    await message.edit("Searching...")
    url = f"{GOOGLE_SEARCH_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_google_results(data["data"])
        search_message = await message.edit(
            f"**Google Search Results for:** `{query}`\n\n{formatted_results}",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        search_key = f"{message.chat.id}_google"
        global search_results
        search_results[search_key] = {
            "results": results,
            "message_id": search_message.id,
        }
        google_url = f"https://www.google.com/search?q={query}"
        await send_screenshot(client, message, google_url)
        asyncio.create_task(
            delete_search_data(client, message.chat.id, search_message.id)
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["ytsearch"], prefix) & filters.me)
async def youtube_search(client: Client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    elif len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    else:
        return await message.edit_text(f"{prefix}ytsearch <query/reply to query>")

    await message.edit("Searching...")
    url = f"{YOUTUBE_SEARCH_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_youtube_results(data["data"])
        search_message = await message.edit(
            f"**YouTube Search Results for:** `{query}`\n\n{formatted_results}",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        search_key = f"{message.chat.id}_youtube"
        global search_results
        search_results[search_key] = {
            "results": results,
            "message_id": search_message.id,
        }
        youtube_url = f"https://www.youtube.com/results?search_query={query}"
        await send_screenshot(client, message, youtube_url)
        asyncio.create_task(
            delete_search_data(client, message.chat.id, search_message.id)
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["moviesearch"], prefix) & filters.me)
async def movie_search(client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    elif len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    else:
        return await message.edit_text(f"{prefix}moviesearch <query/reply to query>")

    await message.edit("Searching...")
    url = f"{MOVIE_SEARCH_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_movie_results(data["data"])

        # Split the message into multiple parts if it's too long
        parts = []
        part_length = 4096  # Telegram's message length limit
        for i in range(0, len(formatted_results), part_length):
            parts.append(formatted_results[i : i + part_length])

        for part in parts:
            search_message = await message.reply(
                f"**Movie Search Results for:** `{query}`\n\n{part}",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

        search_key = f"{message.chat.id}_movie"
        global search_results
        search_results[search_key] = {
            "results": results,
            "message_id": search_message.id,
        }
        asyncio.create_task(
            delete_search_data(client, message.chat.id, search_message.id)
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["apksearch"], prefix) & filters.me)
async def apk_search(client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    elif len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    else:
        return await message.edit_text(f"{prefix}apksearch <query/reply to query>")

    await message.edit("Searching...")
    url = f"{APK_SEARCH_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_apk_results(data["BK9"])
        search_message = await message.edit(
            f"**APK Search Results for:** `{query}`\n\n{formatted_results}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        search_key = f"{message.chat.id}_apk"
        global search_results
        search_results[search_key] = {
            "results": results,
            "message_id": search_message.id,
        }

        asyncio.create_task(
            delete_search_data(client, message.chat.id, search_message.id)
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["wgpt", "gptweb"], prefix) & filters.me)
async def gptweb(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `wgpt <query>`")
        return
    await message.edit("Thinking...")
    query = " ".join(message.command[1:])
    url = f"{URL}/gptweb?text={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        await message.edit(
            f"**Question:**\n{query}\n**Answer:**\n{data['data']}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["wgemini"], prefix) & filters.me)
async def gemini(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `wgemini <query>`")
        return
    await message.edit("Thinking...")
    query = " ".join(message.command[1:])
    url = f"{URL}/gemini?query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        await message.edit(
            f"**Question:**\n{query}\n**Answer:**\n{data['message']}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["sputify"], prefix) & filters.me)
async def spotify_search(client, message: Message):
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else message.reply_to_message.text
    )
    if not query:
        await message.edit("Usage: spotify <query>")
        return
    await search_music(
        f"{BASE_URL}/search/spotify?q=", format_spotify_result, message, query
    )


@Client.on_message(filters.command(["lyrics"], prefix) & filters.me)
async def lyrics_search(client, message: Message):
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else message.reply_to_message.text
    )
    if not query:
        await message.edit("Usage: lyrics <song name>")
        return
    await search_music(
        f"{BASE_URL}/search/letra?query=", format_lyrics_result, message, query
    )


@Client.on_message(filters.command(["soundcloud"], prefix) & filters.me)
async def soundcloud_search(client, message: Message):
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else message.reply_to_message.text
    )
    if not query:
        await message.edit("Usage: soundcloud <query>")
        return
    await search_music(
        f"{BASE_URL}/search/soundcloud?q=", format_soundcloud_result, message, query
    )


@Client.on_message(filters.command(["deezer"], prefix) & filters.me)
async def deezer_search(client, message: Message):
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else message.reply_to_message.text
    )
    if not query:
        await message.edit("Usage: deezer <query>")
        return
    await search_music(
        f"{BASE_URL}/search/deezer?q=", format_deezer_result, message, query
    )


@Client.on_message(filters.command(["applemusic"], prefix) & filters.me)
async def applemusic_search(client, message: Message):
    query = (
        message.text.split(maxsplit=1)[1]
        if len(message.command) > 1
        else message.reply_to_message.text
    )
    if not query:
        await message.edit("Usage: applemusic <query>")
        return
    await search_music(
        f"{BASE_URL}/search/applemusic?text=", format_apple_music_result, message, query
    )


@Client.on_message(filters.reply & filters.text & filters.me)
async def handle_reply(client: Client, message: Message):
    chat_id = message.chat.id
    search_keys = [
        f"{chat_id}_google",
        f"{chat_id}_youtube",
        f"{chat_id}_movie",
        f"{chat_id}_apk",
    ]

    for search_key in search_keys:
        if search_key in search_results:
            try:
                # Check if the replied-to message is one of the bot's search result messages
                if message.reply_to_message.from_user.id != (await client.get_me()).id:
                    return

                index = int(message.text.strip()) - 1
                results = search_results[search_key]["results"]
                search_message_id = search_results[search_key]["message_id"]
                if (
                    message.reply_to_message.id == search_message_id
                    and 0 <= index < len(results)
                ):
                    await message.edit("Please wait...")

                    if search_key.endswith("_movie"):
                        # Send movie details with image
                        movie = results[index]
                        caption = (
                            f"**{movie['title']}** ({movie['release_date']})\n"
                            f"Original Title: {movie['original_title']}\n"
                            f"Language: {movie['original_language']}\n"
                            f"Overview: {movie['overview']}\n"
                            f"Popularity: {movie['popularity']}\n"
                            f"Rating: {movie['vote_average']}/10\n"
                            f"Votes: {movie['vote_count']}"
                        )
                        if "image" in movie:
                            response = requests.get(movie["image"])
                            if response.status_code == 200:
                                with open("movie_image.jpg", "wb") as f:
                                    f.write(response.content)
                                await message.reply_photo(
                                    photo="movie_image.jpg",
                                    caption=caption,
                                    parse_mode=enums.ParseMode.MARKDOWN,
                                )
                                os.remove("movie_image.jpg")
                            else:
                                await message.reply(
                                    caption, parse_mode=enums.ParseMode.MARKDOWN
                                )
                        else:
                            await message.reply(
                                caption, parse_mode=enums.ParseMode.MARKDOWN
                            )
                    elif search_key.endswith("_apk"):
                        apk_url = f"{APK_DOWNLOAD_URL}{results[index]['link']}"
                        fetch_apk_url = requests.get(apk_url)
                        if fetch_apk_url.status_code != 200:
                            await message.edit("Failed to fetch APK data.")
                        else:
                            data_apk = fetch_apk_url.json()
                            download_url = data_apk["BK9"]["link"]
                            size_apk = data_apk["BK9"]["size"]
                            apk_size = float(size_apk.split(" ")[0])

                            if "GB" in size_apk or apk_size > 100:
                                await message.edit(
                                    "File size is too large to download."
                                )
                            else:
                                apk_file_name = f"{data_apk['BK9']['title']}.apk"
                                response = requests.get(download_url)

                                if response.status_code != 200:
                                    await message.edit(
                                        "Failed to download the APK file."
                                    )
                                else:
                                    with open(apk_file_name, "wb") as f:
                                        f.write(response.content)

                                    await message.reply_document(apk_file_name)
                                    os.remove(apk_file_name)
                    else:
                        url = results[index]["url"]
                        await send_screenshot(client, message, url)
                    await message.delete()
                    return
            except ValueError:
                pass


modules_help["sarethai"] = {
    "wgpt [query]*": "Ask anything to GPT-Web",
    "gptweb [query]*": "Ask anything to GPT-Web",
    "wgemini [query]*": "Ask anything to Gemini",
    "sputify [query]*": "Search for songs on Spotify",
    "lyrics [song name]*": "Get the lyrics of a song",
    "soundcloud [query]*": "Search for songs on SoundCloud",
    "deezer [query]*": "Search for songs on Deezer",
    "applemusic [query]*": "Search for songs on Apple Music",
    "gsearch [query]*": "Searches Google for the query.",
    "ytsearch [query]*": "Searches YouTube for the query.",
    "moviesearch [query]*": "Searches movies for the query and returns results.",
    "apksearch [query]*": "Searches APKs for the query and returns results.",
}
