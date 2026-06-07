import urllib.parse
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from utils import modules_help, prefix

async def shorten_url(url: str) -> str:
    # First try da.gd (no preview pages)
    api_url = f"https://da.gd/s?url={urllib.parse.quote(url)}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    short = await response.text()
                    if short:
                        return short.strip()
    except Exception:
        pass
    
    # Fallback to clck.ru (also no preview pages)
    try:
        api_url = f"https://clck.ru/--?url={urllib.parse.quote(url)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    short = await response.text()
                    if short:
                        return short.strip()
    except Exception:
        pass
        
    return url # Return original if all shorteners fail

@Client.on_message(filters.command("lmgtf", prefix) & filters.me)
async def lmgtf_cmd(client: Client, message: Message):
    query = ""
    if len(message.command) > 1:
        query = " ".join(message.command[1:])
    elif message.reply_to_message and message.reply_to_message.text:
        query = message.reply_to_message.text
        
    if not query:
        await message.edit("`Provide a search query or reply to a text message. Example:` `.lmgtf how to do something in water`")
        return
    encoded_query = urllib.parse.quote_plus(query)
    
    # Base URL for let me google that for you
    long_url = f"https://googlethatforyou.com?q={encoded_query}"
    
    hmm = await message.edit("`Finding answer to your question...`")
    
    short_url = await shorten_url(long_url)
    
    text = f"[Here is your answer]({short_url})"
    
    await message.edit(
        text, 
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN
    )

modules_help["lmgtf"] = {
    "lmgtf [query]": "Generates a 'Let Me Google That For You' link for the given query."
}
