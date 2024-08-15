import requests
from pyrogram import Client, filters, enums
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

SEARCH_URL = "https://deliriusapi-official.vercel.app/search"

async def torrentyts(query):
    url = f"{SEARCH_URL}/movieyts?search={query}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and data.get("data"):
            torrents = data["data"]
            result = ""
            for torrent in torrents:
                result += f"**Title:** {torrent.get('title', 'N/A')}\n"
                result += f"**Year:** {torrent.get('year', 'N/A')}\n"
                result += f"**Rating:** {torrent.get('rating', 'N/A')}\n"
                result += f"**Quality:** {torrent.get('quality', 'N/A')}\n"
                result += f"**Type:** {torrent.get('type', 'N/A')}\n"
                result += f"**Is Repack:** {torrent.get('is_repack', 'N/A')}\n"
                result += f"**Video Codec:** {torrent.get('video_codec', 'N/A')}\n"
                result += f"**Bit Depth:** {torrent.get('bit_depth', 'N/A')}\n"
                result += f"**Audio Channels:** {torrent.get('audio_channels', 'N/A')}\n"
                result += f"**Seeds:** {torrent.get('seeds', 'N/A')}\n"
                result += f"**Peers:** {torrent.get('peers', 'N/A')}\n"
                result += f"**Size:** {torrent.get('size', 'N/A')}\n"
                result += f"**Date Uploaded:** {torrent.get('date_uploaded', 'N/A')}\n"
                result += f"**Magnet URL:** {torrent.get('magnet_url', 'N/A')}\n"
                result += f"**Background Image:** {torrent.get('background_image', 'N/A')}\n"
                result += f"**Synopsis:** {torrent.get('synopsis', 'N/A')}\n"
                result += f"**Description Full:** {torrent.get('description_full', 'N/A')}\n"
                result += f"**Summary:** {torrent.get('summary', 'N/A')}\n\n"
            return result
        else:
            return "No information found for this torrent."
    else:
        return "Failed to fetch torrent information."
@Client.on_message(filters.command("yts") prefix& filters.me)
async def ytstorron(client: Client, message: Message):
    query = message.text.split(" ", 1)[1] if len(message.command) > 1 else None
    if not query:
        return await message.reply_text("Give me a movie name")
    try:
        messager = await torrentyts(query)
        if len(messager) > 4096:  # Telegram message size limit
            # Save the large response to a file
            with open("torrent.txt", "w") as f:
                f.write(messager)
            
            # Send the file with a caption
            general_details = "🎥📽️ Here is the torrent information 🦠🧬🌡️"
            await message.reply_document(
                "torrent.txt",
                caption=f"<u><b>General Details</b></u>:\n{general_details}",
            )
            
            # Clean up by removing the file
            os.remove("torrent.txt")
        else:
            await message.reply_text(messager, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

modules_help["yts"] = {"yts": "Get yts torrent information "}
