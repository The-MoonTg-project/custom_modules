import datetime
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
from utils.misc import modules_help, prefix
from pyrogram import Client, filters
from pyrogram.types import Message


now = datetime.datetime.now()
current_month = now.strftime("%b").lower()
current_year = now.year

WEBSITE = [
    "https://www.dailyepaper.in/the-tribune-epaper/",
    f"https://www.dailyepaper.in/economic-times-newspaper-{current_year}/",
    f"https://www.dailyepaper.in/times-of-india-epaper-pdf-{current_month}-{current_year}/#google_vignette",
    "https://www.dailyepaper.in/financial-express-newspaper/",
    "https://www.dailyepaper.in/telegraph-newspaper/",
    "https://www.dailyepaper.in/statesman-newspaper-today/",
]


async def scrape_data(msg):
    errors = ""
    text = ""
    async with aiohttp.ClientSession() as session:
        for url in WEBSITE:
            try:
                data = await session.get(url)
                soup = bs(await data.text(), "html.parser")
                title = soup.find("title").text
                # remove "in PDF download today | DailyEpaper.in" from title
                phrases_to_replace = [
                    "in PDF download today | DailyEpaper.in",
                    "in PDF Free Download Today | DailyEpaper.in",
                    "PDF Free Download Today | DailyEpaper.in",
                    "PDF Free Download | DailyEpaper.in",
                ]
                for phrase in phrases_to_replace:
                    title = title.replace(phrase, "").strip()
                title = title.replace("Today in", "Today").strip()
                title = re.sub(r"\s+", " ", title)
                source = soup.findAll("a", {"target": "_blank", "rel": "noopener"})
                drive_links = [
                    a["href"]
                    for a in source
                    if a["href"].startswith("https://drive.google.com/")
                ]

                if title and drive_links:
                    await msg.edit_text(
                        f"✅ Scraping from <b>{title}</b> was successful."
                    )
                    text += f"<b>{title}</b> - <pre>{drive_links[0]}</pre>\n"

            except Exception as e:
                await msg.edit_text(f"❌ Scraping from <b>{url}</b> was unsuccessful.")
                errors += f"{url}: {repr(e)}\n\n"
            await asyncio.sleep(5)
    return text, errors


@Client.on_message(filters.command(["epaper", "dailyepaper"], prefix) & filters.me)
async def scrape_command(client: Client, message: Message):
    await message.edit_text("🔄 Starting to scrape data...")
    text, errors = await scrape_data(message)
    if text:
        await message.edit_text(f"✅ Scraping complete:\n\n{text}")
    if errors:
        await message.edit_text(f"⚠️ Errors encountered:\n\n{errors}")


modules_help["dailyepaper"] = {
    "epaper": "get daily news paper (english only)",
    "dailyepaper": "get daily news paper (english only)"
}
