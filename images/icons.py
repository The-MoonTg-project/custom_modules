import re
import requests
import random
from io import BytesIO
from bs4 import BeautifulSoup as bs

from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import RPCError

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("icon", prefix) & filters.me)
async def search_icon(_, message: Message):
    if not len(message.command) == 2:
        return await message.edit_text(
            "Please provide some text to search icons from Flaticon.com."
        )
    query = message.text.split(maxsplit=1)[1]

    await message.edit_text("Searching for icons...")
    search_query = query.replace(" ", "%20")
    url = f"https://www.flaticon.com/search?word={search_query}"

    try:
        html_content = requests.get(url).text
        soup = bs(html_content, "html.parser")
        results = soup.find_all(
            "img",
            src=re.compile(r"https://cdn-icons-png.flaticon.com/128/[0-9]+/[0-9]+.png"),
        )

        if not results:
            return await message.edit("No results found.")

        random.shuffle(results)
        icons = []
        for i in range(5):
            icons.append(results[i]["src"].replace("128", "512"))

        for icon in icons:
            await message.reply_document(icon)

        return await message.delete()
    except Exception as e:
        await message.edit(f"An error occurred: {e}")
        print(f"Error: {e}")


@Client.on_message(filters.command("freepik", prefix) & filters.me)
async def freepik_search(client: Client, message: Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.edit_text("Please provide a search query!")
        return

    query = parts[1]
    limit = 5
    if " ; " in query:
        match, limit_str = query.split(" ; ", 1)
        try:
            limit = int(limit_str)
        except ValueError:
            await message.edit_text("Invalid limit! Using the default value of 5.")
    else:
        match = query

    match = match.replace(" ", "%20")
    await message.edit_text("Searching Freepik...")

    try:
        url = f"https://www.freepik.com/api/regular/search?locale=en&term={match}"
        json_content = requests.get(url).json()
        results = []
        for i in json_content["items"]:
            results.append(i["preview"]["url"])

        if results is None:
            return await message.edit_text("No results found.")

        random.shuffle(results)
        img_urls = results[:limit]

        media_group = []
        for img_url in img_urls:
            icon = requests.get(img_url)
            if icon.status_code == 200:
                media_group.append(InputMediaPhoto(media=BytesIO(icon.content)))

        if not media_group:
            await message.edit_text("No images could be downloaded.")
            return

        try:
            await client.send_media_group(chat_id=message.chat.id, media=media_group)
        except RPCError:
            await message.edit_text(
                "Failed to send some images. Retrying individually..."
            )
            for media in media_group:
                try:
                    await message.reply_photo(photo=media.media)
                except Exception as e:
                    await message.edit_text(f"Error sending image: {e}")

    except Exception as e:
        await message.edit_text(f"Failed to fetch data: {e}")
        print(f"Error: {e}")


modules_help["icons"] = {
    "icon [query]": "Search for icons on Flaticon.",
    "freepik [query] [limit]": "Search for images on Freepik. Limit is optional and defaults to 5.",
}
