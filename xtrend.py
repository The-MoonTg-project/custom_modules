from pyrogram import Client, filters
from bs4 import BeautifulSoup
import aiohttp
import random

from utils.misc import modules_help, prefix


def get_ua():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    ]
    return random.choice(user_agents)


async def get_trendings(country):
    base_url = "https://getdaytrends.com"
    if country:
        url = f"{base_url}/{country}"
    else:
        url = base_url
    headers = {"user-agent": get_ua()}

    def get_result(data):
        tags = data.table.find_all("tr")
        results = []
        for tr in tags:
            src = tr.td
            title = src.get_text()
            link = base_url + src.a.get("href")
            results.append({"title": title, "url": link})
        return results

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {"error": response.reason}
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                tables = soup.select("div[class^='inset']")
                return {
                    "now_hashtags": get_result(tables[0]),
                    "today_hashtags": get_result(tables[1]),
                    "top_hashtags": get_result(tables[2]),
                }
        except Exception as e:
            return {"error": str(e)}


@Client.on_message(filters.command("xtrend", prefix) & filters.me)
async def trend_command(client, message):
    country = None
    if len(message.command) == 2:
        country = message.command[1].lower()

    await message.edit("<b>Getting X(Twitter) Trends...</b>")
    trends = await get_trendings(country)

    if "error" in trends:
        await message.reply(f"Error: {trends['error']}")
        return

    response = (
        f"<b>Trending Hashtags {country.upper() if country else 'Worldwide'}</b>\n\n"
    )

    response += "<b>Now Trending:</b>\n"
    for tag in trends["now_hashtags"]:
        response += f"- <a href='{tag['url']}'>{tag['title']}</a>\n"

    response += "\n<b>Top Hashtags Most Tweeted last <code>24h</code>:</b>\n"
    for tag in trends["today_hashtags"]:
        response += f"- <a href='{tag['url']}'>{tag['title']}</a>\n"

    response += "\n<b>Top Hashtags Longest Trending:</b>\n"
    for tag in trends["top_hashtags"]:
        response += f"- <a href='{tag['url']}'>{tag['title']}</a>\n"

    await message.reply(response, disable_web_page_preview=True)


modules_help["xtrend"] = {
    "xtrend [country]": "get latest twitter trading of a country "
    "if no country is given then it will show global trending",
}
