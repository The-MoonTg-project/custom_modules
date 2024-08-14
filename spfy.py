import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from io import BytesIO
import asyncio

from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# Function to perform Spotify search using the provided API
def spotify_search(query):
    url = f'https://deliriusapi-official.vercel.app/search/spotify?q={requests.utils.quote(query)}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get('data')
        if isinstance(data, list):
            return data
    return None

# Function to get Spotify download link using the provided API
def get_spotify_download_link(track_url):
    url = f'https://tools.betabotz.eu.org/tools/spotifydl?url={requests.utils.quote(track_url)}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('result')
    return None

# Dictionary to store search results
search_results = {}

@Client.on_message(filters.command("spfy", prefix) & filters.me)
async def spotify_search_command(client, message: Message):
    try:
        # Check if the command is a reply to another message
        if message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        else:
            command_parts = message.text.split(' ', 1)
            if len(command_parts) < 2:
                await message.reply_text("Please provide a search query after the command or reply to a message containing the search query.")
                return
            query = command_parts[1]

        results = spotify_search(query)
        if not results:
            await message.reply_text("No results found.")
            return

        # Edit the original command message to "Please wait..."
        await message.edit_text("Please wait...")

        result_text = f"**Spotify Search Results for:** _{query}_\n\n"
        for i, result in enumerate(results[:15]):  # Limit to 15 results
            result_text += (f"{i+1}. **{result.get('title', 'Unknown')}** by **{result.get('artist', 'Unknown')}**\n"
                            f"Album: {result.get('album', 'Unknown')}\n"
                            f"Duration: {result.get('duration', 'Unknown')}\n"
                            f"Popularity: {result.get('popularity', 'Unknown')}\n"
                            f"Published: {result.get('publish', 'Unknown')}\n"
                            f"[Listen on Spotify]({result.get('url', '#')})\n\n")

        # Store search results with message id as key
        search_results[message.chat.id] = {i+1: result.get('url', '') for i, result in enumerate(results)}

        # Update the message with search results
        result_message = await message.edit_text(result_text, parse_mode=enums.ParseMode.MARKDOWN)
        
        # Schedule deletion of the message and cleanup of the search results
        await asyncio.sleep(60)
        await result_message.delete()
        
        # Remove search results entry if it exists
        search_results.pop(message.chat.id, None)
    
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

@Client.on_message(filters.reply & filters.me)
async def download_spotify_song(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            chat_id = message.chat.id
            if chat_id in search_results:
                try:
                    selected_number = int(message.text.strip())
                except ValueError:
                    return  # Ignore invalid song numbers

                if selected_number in search_results[chat_id]:
                    track_url = search_results[chat_id][selected_number]
                    download_link = get_spotify_download_link(track_url)
                    if download_link:
                        # Edit the song number message to "Please wait..."
                        await message.edit_text("Please wait...")

                        # Download the song
                        response = requests.get(download_link)
                        if response.status_code == 200:
                            song_data = BytesIO(response.content)
                            song_data.name = f"{selected_number}.mp3"

                            # Upload the song to Telegram
                            await client.send_audio(
                                chat_id=message.chat.id,
                                audio=song_data,
                                caption=""  # Remove the caption
                            )

                        # Delete the "Please wait..." message after sending the song
                        await message.delete()
                    else:
                        await message.reply_text("Failed to get the download link.")
                else:
                    await message.reply_text("Invalid song number.")
    
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

modules_help["spotify"] = {
    "spfy [search query]": "Searches and downloads Spotify Music",
}
