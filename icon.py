import os
import random
from bs4 import BeautifulSoup as bs
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InputMediaPhoto
from utils.misc import modules_help, prefix
import re
import random
from urllib.request import urlopen


from pyrogram.errors import RPCError


async def async_searcher(url: str):
    """Fetch HTML content of the given URL."""
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def download_file(url: str, file_name: str):
    """Download file from URL and save locally."""
    async with ClientSession() as session:
        async with session.get(url) as response:
            with open(file_name, "wb") as f:
                f.write(await response.read())


@Client.on_message(filters.command("icon", prefix) & filters.me)
async def search_icon(client: Client, message: Message):
    """Handle the {prefix}icon command."""
    query = message.text.split(" ", 1)[-1]
    
    if not query or query == "{prefix}icon":
        return await message.reply("Please provide some text to search icons from Flaticon.com.")
    
    searching_msg = await message.reply("Searching for icons...")
    search_query = query.replace(" ", "%20")
    url = f"https://www.flaticon.com/search?word={search_query}"
    
    try:
        # Fetch and parse Flaticon search results
        html_content = await async_searcher(url)
        soup = bs(html_content, "html.parser")
        results = soup.find_all("img", {"data-src": True})  # Updated to check for icons with 'data-src'

        if not results:
            return await searching_msg.edit("No results found.")
        
        # Select a random icon and download
        random_icon = results[random.randint(0, len(results) - 1)]["data-src"]
        file_name = "icon.png"
        await download_file(random_icon, file_name)
        
        # Send the icon to the user
        await message.reply_document(file_name)
        os.remove(file_name)
        await searching_msg.delete()
    except Exception as e:
        await searching_msg.edit("An error occurred. Please try again later.")
        print(f"Error: {e}")






@Client.on_message(filters.command("freepik", prefix)& filters.me)
async def freepik_search(client, message):
    # Parsing user input
    query = message.text.split(maxsplit=1)
    if len(query) < 2:
        await message.reply_text("Please provide a search query!")
        return

    match = query[1]
    limit = 5  # Default limit
    if " ; " in match:
        match, limit_str = match.split(" ; ", maxsplit=1)
        try:
            limit = int(limit_str)
        except ValueError:
            await message.reply_text("Invalid limit! Using the default value of 5.")
            limit = 5

    match = match.replace(" ", "%20")
    await message.reply_text("Searching Freepik...")

    # Fetching Freepik images
    try:
        content = urlopen(f"https://www.freepik.com/search?format=search&page=1&query={match}")
        soup = bs(content, "html.parser", from_encoding="utf-8")
        results = soup.find_all("img", src=re.compile(r"img\.freepik\.com"))
    except Exception as e:
        await message.reply_text(f"Failed to fetch data: {e}")
        return

    if not results:
        await message.reply_text("No results found!")
        return

    # Shuffle and limit results
    random.shuffle(results)
    img_urls = [img["src"] for img in results[:limit]]

    # Download images
    downloaded_images = []
    for img_url in img_urls:
        try:
            response = urlopen(img_url)
            downloaded_images.append(response.read())
        except Exception as e:
            await message.reply_text(f"Failed to download image: {e}")

    if not downloaded_images:
        await message.reply_text("No images could be downloaded.")
        return

    # Send images with spoiler support
    media = [InputMediaPhoto(media=img_bytes, has_spoiler=True) for img_bytes in downloaded_images if img_bytes]
    try:
        await app.send_media_group(
            chat_id=message.chat.id,
            media=media
        )
    except RPCError:
        await message.reply_text("Failed to send some images. Retrying individually...")
        for img_bytes in downloaded_images:
            try:
                await message.reply_photo(photo=img_bytes, has_spoiler=True)
            except Exception as e:
                await message.reply_text(f"Error sending image: {e}")


  
modules_help["icon"] = {
    "ico.": "simply icon search",
    "freepik.": "simply freepik search",
}
