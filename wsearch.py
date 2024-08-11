import os
import requests
import asyncio
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# API URLs
GOOGLE_SEARCH_URL = "https://deliriusapi-official.vercel.app/search/googlesearch?query="
YOUTUBE_SEARCH_URL = "https://deliriusapi-official.vercel.app/search/ytsearch?q="
MOVIE_SEARCH_URL = "https://deliriusapi-official.vercel.app/search/movie?query="
APK_SEARCH_URL = "https://api.maher-zubair.tech/search/apk?q="
APK_DOWNLOAD_URL = "https://api.maher-zubair.tech/download/apk?id="
SCREENSHOT_API_URL = "https://api.apiflash.com/v1/urltoimage?access_key=806cf941653948be8d8049defd086b82&url={query}&format=jpeg&full_page=true&no_cookie_banners=true&no_ads=true&no_tracking=true"

# Store search results temporarily
search_results = {}

# Helper Functions
def format_google_results(results):
    results = results[:15]
    return results, "\n\n".join([f"{i+1}. **[{item['title']}]({item['url']})**\n{item['description']}" for i, item in enumerate(results)])

def format_youtube_results(results):
    results = results[:15]
    return results, "\n\n".join([f"{i+1}. **[{item['title']}]({item['url']})**\nPublished by: [{item['author']['name']}]({item['author']['url']}) - {item['views']} views - {item['duration']}" for i, item in enumerate(results)])

def format_movie_results(results):
    results = results[:15]
    return results, "\n\n".join([f"{i+1}. **{item['title']}** ({item['release_date']})\nRating: {item['vote_average']}/10\nVotes: {item['vote_count']}" for i, item in enumerate(results)])

def format_apk_results(results):
    results = results[:15]
    return results, "\n\n".join([f"{i+1}. **{item['name']}**\nID: {item['id']}" for i, item in enumerate(results)])

async def send_screenshot(message, url):
    screenshot_url = SCREENSHOT_API_URL.format(query=url)
    response = requests.get(screenshot_url)
    if response.status_code == 200:
        screenshot_path = "screenshot.jpg"
        with open(screenshot_path, "wb") as f:
            f.write(response.content)
        await message.reply_document(screenshot_path)
        os.remove(screenshot_path)
    else:
        await message.reply("Failed to take screenshot.")

async def delete_search_data(client, chat_id, message_id):
    await asyncio.sleep(60)
    for key in ["google", "youtube", "movie", "apk"]:
        search_key = f"{chat_id}_{key}"
        if search_key in search_results and search_results[search_key]['message_id'] == message_id:
            del search_results[search_key]
            try:
                await client.delete_messages(chat_id, message_id)
            except:
                pass
            break

# Command Handlers
@Client.on_message(filters.command(["gsearch"], prefix) & filters.me)
async def google_search(client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    else:
        if (query := message.text[len("/gsearch "):].strip()) == "":
            await message.edit("Usage: `gsearch <query>`")
            return

    await message.edit("Searching...")
    url = f"{GOOGLE_SEARCH_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_google_results(data["data"])
        search_message = await message.edit(
            f"**Google Search Results for:** `{query}`\n\n{formatted_results}",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        search_key = f"{message.chat.id}_google"
        search_results[search_key] = {'results': results, 'message_id': search_message.id}
        google_url = f"https://www.google.com/search?q={query}"
        await send_screenshot(message, google_url)
        asyncio.create_task(delete_search_data(client, message.chat.id, search_message.id))
    else:
        await message.edit("An error occurred, please try again later.")

# Repeat similarly for other search commands (youtube, movie, apk)

@Client.on_message(filters.command(["ytsearch"], prefix) & filters.me)
async def youtube_search(client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    else:
        if (query := message.text[len("/ytsearch "):].strip()) == "":
            await message.edit("Usage: `ytsearch <query>`")
            return

    await message.edit("Searching...")
    url = f"{YOUTUBE_SEARCH_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_youtube_results(data["data"])
        search_message = await message.edit(
            f"**YouTube Search Results for:** `{query}`\n\n{formatted_results}",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        search_key = f"{message.chat.id}_youtube"
        search_results[search_key] = {'results': results, 'message_id': search_message.id}
        youtube_url = f"https://www.youtube.com/results?search_query={query}"
        await send_screenshot(message, youtube_url)
        asyncio.create_task(delete_search_data(client, message.chat.id, search_message.id))
    else:
        await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["moviesearch"], prefix) & filters.me)
async def movie_search(client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    else:
        if (query := message.text[len("/moviesearch "):].strip()) == "":
            await message.edit("Usage: `moviesearch <query>`")
            return

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
            parts.append(formatted_results[i:i + part_length])

        for part in parts:
            search_message = await message.reply(
                f"**Movie Search Results for:** `{query}`\n\n{part}",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

        search_key = f"{message.chat.id}_movie"
        search_results[search_key] = {'results': results, 'message_id': search_message.id}
        asyncio.create_task(delete_search_data(client, message.chat.id, search_message.id))
    else:
        await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["apksearch"], prefix) & filters.me)
async def apk_search(client, message: Message):
    if message.reply_to_message:
        query = message.reply_to_message.text.strip()
    else:
        if (query := message.text[len("/apksearch "):].strip()) == "":
            await message.edit("Usage: `apksearch <query>`")
            return

    await message.edit("Searching...")
    url = f"{APK_SEARCH_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_apk_results(data["result"])
        search_message = await message.edit(
            f"**APK Search Results for:** `{query}`\n\n{formatted_results}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        search_key = f"{message.chat.id}_apk"
        search_results[search_key] = {'results': results, 'message_id': search_message.id}

        # Download the APK file
        download_url = f"https://api.maher-zubair.tech/download/apk?id={query}"
        response = requests.get(download_url)
        if response.status_code == 200:
            apk_data = response.json()
            apk_file_url = apk_data["result"]["dllink"]
            apk_file_name = f"{apk_data['result']['name']}.apk"
            apk_response = requests.get(apk_file_url)
            if apk_response.status_code == 200:
                with open(apk_file_name, "wb") as f:
                    f.write(apk_response.content)

                # Upload the APK file to Telegram
                await message.reply_document(apk_file_name)

                # Delete the APK file from the server
                os.remove(apk_file_name)
            else:
                await message.edit("Failed to download the APK file.")
        else:
            await message.edit("Failed to retrieve the APK download link.")

        asyncio.create_task(delete_search_data(client, message.chat.id, search_message.id))
    else:
        await message.edit("An error occurred, please try again later.")

# Handler for replies with a number
@Client.on_message(filters.reply & filters.text & filters.me)
async def handle_reply(client, message: Message):
    chat_id = message.chat.id
    search_keys = [f"{chat_id}_google", f"{chat_id}_youtube", f"{chat_id}_movie", f"{chat_id}_apk"]

    for search_key in search_keys:
        if search_key in search_results:
            try:
                # Check if the replied-to message is one of the bot's search result messages
                if message.reply_to_message.from_user.id != (await client.get_me()).id:
                    return

                index = int(message.text.strip()) - 1
                results = search_results[search_key]['results']
                search_message_id = search_results[search_key]['message_id']
                if message.reply_to_message.id == search_message_id and 0 <= index < len(results):
                    await message.edit("Please wait...")  # Edit the reply message to show "Please wait..."

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
                        if 'image' in movie:
                            response = requests.get(movie['image'])
                            if response.status_code == 200:
                                with open("movie_image.jpg", "wb") as f:
                                    f.write(response.content)
                                await message.reply_photo(photo="movie_image.jpg", caption=caption, parse_mode=enums.ParseMode.MARKDOWN)
                                os.remove("movie_image.jpg")
                            else:
                                await message.reply(caption, parse_mode=enums.ParseMode.MARKDOWN)
                        else:
                            await message.reply(caption, parse_mode=enums.ParseMode.MARKDOWN)
                    elif search_key.endswith("_apk"):
                        apk_id = results[index]['id']
                        download_url = f"{APK_DOWNLOAD_URL}{apk_id}"
                        response = requests.get(download_url)
                        if response.status_code == 200:
                            apk_data = response.json()
                            apk_name = apk_data['result']['name']
                            apk_link = apk_data['result']['dllink']
                            apk_file = requests.get(apk_link)
                            if apk_file.status_code == 200:
                                apk_path = f"{apk_name}.apk"
                                with open(apk_path, "wb") as f:
                                    f.write(apk_file.content)
                                await message.reply_document(apk_path)
                                os.remove(apk_path)
                            else:
                                await message.reply("Failed to download APK.")
                        else:
                            await message.reply("Failed to fetch APK download link.")
                    else:
                        url = results[index]['url']
                        await send_screenshot(message, url)
                    await message.delete()  # Delete the "Please wait..." message
                    return
            except ValueError:
                pass

# Module Help
modules_help["search"] = {
    "gsearch [query]*": "Searches Google for the query.",
    "ytsearch [query]*": "Searches YouTube for the query.",
    "moviesearch [query]*": "Searches movies for the query and returns results.",
    "apksearch [query]*": "Searches APKs for the query and returns results.",
}
