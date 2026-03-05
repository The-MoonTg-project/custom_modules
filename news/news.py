import random

import aiohttp
from pyrogram import Client, filters
from utils.scripts import format_exc

from utils import modules_help, prefix

NEWS_URL = "https://sugoi-api.vercel.app/news?keyword={}"


@Client.on_message(filters.command("news", prefix) & filters.me)
async def enews(_, message):
    keyword = (
        message.text.split(" ", 1)[1].strip() if len(message.text.split()) > 1 else ""
    )
    url = NEWS_URL.format(keyword)
    await message.edit_text("Fetching news...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                news_data = await resp.json()

        if "error" in news_data:
            error_message = news_data["error"]
            await message.edit_text(f"Error: {error_message}")
        else:
            if len(news_data) > 0:
                news_item = random.choice(news_data)

                title = news_item["title"]
                excerpt = news_item["excerpt"]
                source = news_item["source"]
                relative_time = news_item["relative_time"]
                news_url = news_item["url"]

                message_text = f"𝗧𝗜𝗧𝗟𝗘: {title}\n𝗦𝗢𝗨𝗥𝗖𝗘: {source}\n𝗧𝗜𝗠𝗘: {relative_time}\n𝗘𝗫𝗖𝗘𝗥𝗣𝗧: {excerpt}\n𝗨𝗥𝗟: {news_url}"
                await message.edit_text(message_text)
            else:
                await message.edit_text("No news found.")

    except Exception as e:  # Replace with specific exception type if possible
        return await message.edit_text(format_exc(e))


modules_help["news"] = {
    "news": "Gets the news of a  catagory."
    + f"\n\nUsage: <code>{prefix}news <catagory> </code>"
    + f"\n\nExample: <code>{prefix}news political</code>"
}
