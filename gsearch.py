import os
import requests
import asyncio
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

GOOGLE_SEARCH_URL = "https://deliriussapi-oficial.vercel.app/search/googlesearch?query="
SCREENSHOT_API_URL = (
    "https://api.apiflash.com/v1/urltoimage?access_key=806cf941653948be8d8049defd086b82&url={query}"
    "&format=jpeg&full_page=true&no_cookie_banners=true&no_ads=true&no_tracking=true"
)
RESULT_EXPIRY_SECONDS = 60
search_results = {}

def format_google_results(results):
    results = results[:5]
    return results, "\n\n".join(
        [f"{i+1}. **[{item['title']}]({item['url']})**\n{item['description']}" for i, item in enumerate(results)]
    )

async def send_screenshot(message, url):
    response = requests.get(SCREENSHOT_API_URL.format(query=url))
    if response.status_code == 200:
        with open("webshot.jpg", "wb") as f:
            f.write(response.content)
        await message.reply_document("webshot.jpg")
        os.remove("webshot.jpg")
    else:
        await message.reply("Failed to take screenshot.")

async def cleanup_expired_results():
    while True:
        await asyncio.sleep(60)
        current_time = asyncio.get_event_loop().time()
        expired_keys = [
            key for key, value in search_results.items()
            if current_time - value["timestamp"] > RESULT_EXPIRY_SECONDS
        ]
        for key in expired_keys:
            del search_results[key]

@Client.on_message(filters.command("google", prefix) & filters.me)
async def google_search(client, message: Message):
    query = (
        message.reply_to_message.text.strip()
        if message.reply_to_message
        else message.text[len("google "):].strip()
    )
    if not query:
        await message.edit("Usage: `google <query>`")
        return
    await message.edit("Searching...")
    response = requests.get(f"{GOOGLE_SEARCH_URL}{query}")
    if response.status_code == 200:
        data = response.json()
        results, formatted_results = format_google_results(data["data"])
        search_message = await message.edit(
            f"**Google Search Results for:** `{query}`\n\n{formatted_results}",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        search_results[f"{message.chat.id}_google"] = {
            "results": results,
            "message_id": search_message.id,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await send_screenshot(message, f"https://www.google.com/search?q={query}")
    else:
        await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.reply & filters.text & filters.me)
async def handle_reply(client, message: Message):
    search_key = f"{message.chat.id}_google"
    if search_key in search_results:
        try:
            if message.reply_to_message.id != search_results[search_key]["message_id"]:
                return
            index = int(message.text.strip()) - 1
            results = search_results[search_key]["results"]
            if 0 <= index < len(results):
                await message.edit("Please wait...")
                await send_screenshot(message, results[index]["url"])
                await message.delete()
            else:
                await message.reply("Invalid selection. Please reply with a valid number.")
        except (ValueError, IndexError):
            await message.reply("Invalid input. Please reply with a valid number.")

asyncio.create_task(cleanup_expired_results())

modules_help["search"] = {
    "gsearch [query]*": "Search Google for the query.",
    "Reply with a number": "Fetch details for the selected search result.",
}
