import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
from utils.misc import modules_help, prefix
from pyrogram import Client, filters, enums
from pyrogram.types import Message

#
#only Eng language epaper work 
# List of websites to scrape
WEBSITE = [
    "https://www.dailyepaper.in/the-tribune-epaper/",
    "https://www.dailyepaper.in/economic-times-newspaper-2024/",
    "https://www.dailyepaper.in/times-of-india-epaper-pdf-aug-2024/#google_vignette",
    "https://www.dailyepaper.in/financial-express-newspaper/",
    "https://www.dailyepaper.in/telegraph-newspaper/",
    "https://www.dailyepaper.in/statesman-newspaper-today/",
    
]


# Command to start scraping

async def scrape_data(msg: Message):
    errors = ""
    text = ""
    async with aiohttp.ClientSession() as session:
        for url in WEBSITE:
            try:
                data = await session.get(url)
                soup = bs(await data.text(), "html.parser")
                title = soup.find('title').text
                source = soup.findAll('a', {'target': '_blank', 'rel': 'noopener'})
                drive_links = [a['href'] for a in source if a['href'].startswith('https://drive.google.com/')]

                if title and drive_links:
                    await msg.reply_text(f"✅ Scraping from {title} was successful.")
                    text += f"{title} - {drive_links[0]}\n\n"

            except Exception as e:
                await msg.reply_text(f"❌ Scraping from {url} was unsuccessful.")
                errors += f"{url}: {repr(e)}\n\n"
            await asyncio.sleep(5)
    return text, errors


@Client.on_message(filters.command(["epaper", "enews"], prefix) & filters.me)
async def scrape_command(client: Client, message: Message):
    await message.reply_text("🔄 Starting to scrape data...")
    text, errors = await scrape_data(message)
    if text:
        await message.reply_text(f"✅ Scraping complete:\n\n{text}")
    if errors:
        await message.reply_text(f"⚠️ Errors encountered:\n\n{errors}")


      modules_help["news"] = {
    "epaper": "get daily news paper (english only)",
    "epaper": ,
      }
# 
