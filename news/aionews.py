import os
import requests
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from modules.url import generate_screenshot

API_CONFIGS = {
    "currents": {
        "api_key": "2HMtAB0LQkQU1HJ4jUb2d-Iemm6HkEETi2AYOQkZWADZSw7L",
        "url": "https://api.currentsapi.services/v1/latest-news",
        "params_key": "country",
        "results_key": "news",
        "status_key": "status",
        "status_ok_value": "ok",
        "date_key": "published",
        "url_key": "url",
    },
    "gnews": {
        "api_key": "76dbbaa53b7bcb176d58e4b5d72fc8db",
        "url": "https://gnews.io/api/v4/top-headlines",
        "params_key": "country",
        "results_key": "articles",
        "status_key": "totalArticles",
        "status_ok_value": lambda x: x > 0,
        "date_key": "publishedAt",
        "url_key": "url",
    },
    "newsdata": {
        "api_key": "pub_498795c6c31ca3c49fb7aaef3a7e5925f4c18",
        "url": "https://newsdata.io/api/1/news",
        "params_key": "country",
        "results_key": "results",
        "status_key": "results",
        "status_ok_value": lambda x: len(x) > 0,
        "date_key": "pubDate",
        "url_key": "link",
    },
    "newsapi": {
        "api_key": "cc005a768fff41e8acf1cb48ac8b738c",
        "url": "https://newsapi.org/v2/top-headlines",
        "params_key": "country",
        "results_key": "articles",
        "status_key": "totalResults",
        "status_ok_value": lambda x: x > 0,
        "date_key": "publishedAt",
        "url_key": "url",
    },
}

# Store search results temporarily
news_search_results = {}

SCREENSHOT_API_URL = "https://api.screenshotone.com/take?access_key=sEfJjC_6S1D9FQ&url={query}&viewport_width=1920&viewport_height=1080&device_scale_factor=1&image_quality=80&format=jpg&block_ads=true&block_cookie_banners=true&full_page=false&block_trackers=true&block_banners_by_heuristics=false&delay=0&timeout=60"


def format_headlines(articles, api_config):
    return articles, "\n\n".join(
        [
            f"{i+1}. **{article['title']}**\n{article.get('description', 'No description')}\nPublished on: {article.get(api_config['date_key'], 'Unknown date')}\n[Read More]({article.get(api_config['url_key'], '#')})"
            for i, article in enumerate(articles[:10])
        ]
    )


async def send_long_message(message, text):
    max_length = 4096
    if len(text) <= max_length:
        await message.edit(
            text, parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True
        )
    else:
        parts = [text[i : i + max_length] for i in range(0, len(text), max_length)]
        await message.edit(
            parts[0], parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True
        )
        for part in parts[1:]:
            await message.reply(
                part, parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True
            )


async def send_screenshot(client, message, url):
    screenshot_url = SCREENSHOT_API_URL.format(query=url)
    screenshot_data = generate_screenshot(url)
    if screenshot_data:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=screenshot_data,
            caption=f"screenshot of <code>{url}</code>",
        )
    else:
        await message.reply("Failed to take screenshot.")


async def fetch_news(api_name, country_code, message):
    api_config = API_CONFIGS[api_name]
    params = {
        api_config["params_key"]: country_code,
        "apiKey" if api_name != "gnews" else "token": api_config["api_key"],
    }
    response = requests.get(api_config["url"], params=params)
    if response.status_code == 200:
        news_data = response.json()
        status = news_data[api_config["status_key"]]
        if (
            status == api_config["status_ok_value"]
            if isinstance(api_config["status_ok_value"], str)
            else api_config["status_ok_value"](status)
        ):
            articles, headlines = format_headlines(
                news_data[api_config["results_key"]], api_config
            )
            search_message = await send_long_message(
                message,
                f"**Top {api_name.capitalize()} Headlines for {country_code.upper()}:**\n\n{headlines}",
            )
            global news_search_results
            news_search_results[f"{message.chat.id}_{api_name}"] = {
                "results": articles,
                "message_id": search_message.id,
            }
        else:
            await message.edit(
                f"No {api_name.capitalize()} articles found for {country_code}."
            )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["aionews"], prefix) & filters.me)
async def get_news(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `news <country_code>`")
        return
    await message.edit(f"Fetching news headlines for {message.command[1]}...")
    try:
        await fetch_news("currents", message.command[1], message)
    except AttributeError:
        pass


@Client.on_message(filters.command(["aio_gnews"], prefix) & filters.me)
async def get_gnews(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `gnews <country_code>`")
        return
    await message.edit(f"Fetching GNews headlines for {message.command[1]}...")
    try:
        await fetch_news("gnews", message.command[1], message)
    except AttributeError:
        pass


@Client.on_message(filters.command(["aio_newsdata"], prefix) & filters.me)
async def get_newsdata(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `newsdata <country_code>`")
        return
    await message.edit(f"Fetching NewsData headlines for {message.command[1]}...")
    try:
        await fetch_news("newsdata", message.command[1], message)
    except AttributeError:
        pass


@Client.on_message(filters.command(["aio_newsapi"], prefix) & filters.me)
async def get_newsapi(_, message: Message):
    if len(message.command) < 2:
        await message.edit(f"Usage: <code>{prefix}newsapi <country_code></code>")
        return
    await message.edit(f"Fetching NewsAPI headlines for {message.command[1]}...")
    try:
        await fetch_news("newsapi", message.command[1], message)
    except AttributeError:
        pass


# Handler for replies with a number
@Client.on_message(filters.reply & filters.me & filters.text)
async def handle_aio_reply(client: Client, message: Message):
    chat_id = message.chat.id
    search_keys = [
        f"{chat_id}_currents",
        f"{chat_id}_gnews",
        f"{chat_id}_newsdata",
        f"{chat_id}_newsapi",
    ]

    for search_key in search_keys:
        global news_search_results
        if search_key in news_search_results:
            try:
                if message.reply_to_message.from_user.id != (await client.get_me()).id:
                    return

                index = int(message.text.strip()) - 1
                results = news_search_results[search_key]["results"]
                search_message_id = news_search_results[search_key]["message_id"]
                if (
                    message.reply_to_message.id == search_message_id
                    and 0 <= index < len(results)
                ):
                    await message.edit("Please wait...")
                    url = results[index]["url"]
                    await send_screenshot(client, message, url)
                    await message.delete()
                    return
            except ValueError:
                pass


modules_help["aionews"] = {
    "aionews [country_code]*": "Fetch and display the latest news headlines for the specified country code using Currents API.",
    "aio_gnews [country_code]*": "Fetch and display the latest news headlines for the specified country code using GNews API.",
    "aio_newsdata [country_code]*": "Fetch and display the latest news headlines for the specified country code using NewsData API.",
    "aio_newsapi [country_code]*": "Fetch and display the latest news headlines for the specified country code using NewsAPI.",
}
