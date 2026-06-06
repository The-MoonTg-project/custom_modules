import re
import bs4
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix

@Client.on_message(filters.command(["app"], prefix) & filters.me)
async def send_app(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("`Provide an app name to search.`")
        return
        
    args = message.command[1:]
    gl = "IN"
    
    if args[0].startswith("-") and len(args[0]) == 3:
        gl = args[0][1:].upper()
        app_name = " ".join(args[1:])
    else:
        app_name = " ".join(args)
        
    if not app_name:
        await message.edit("`Provide an app name to search.`")
        return
        
    mg = await message.edit(f"`Searching Play Store ({gl})...`")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://play.google.com/store/search?q={app_name}&c=apps&gl={gl}&hl=en", headers=headers) as page:
                content = await page.text()
                
            soup = bs4.BeautifulSoup(content, 'html.parser')
            links = soup.find_all('a', href=re.compile(r'/store/apps/details\?id='))
            
            if not links:
                await mg.edit("`No apps found for this query.`")
                return
                
            app_link = "https://play.google.com" + links[0]['href']
            
            async with session.get(f"{app_link}&gl={gl}&hl=en", headers=headers) as detail_page:
                d_content = await detail_page.text()
                
            dsoup = bs4.BeautifulSoup(d_content, 'html.parser')
            
            name_tag = dsoup.find('h1', itemprop="name")
            name = name_tag.text if name_tag else dsoup.h1.text if dsoup.h1 else 'Unknown'
            
            dev_tag = dsoup.find('a', href=re.compile(r'/store/apps/dev\?id=|/store/apps/developer\?id='))
            dev = dev_tag.text if dev_tag else 'Unknown'
            dev_link = "https://play.google.com" + dev_tag['href'] if dev_tag else app_link
            
            img_tag = dsoup.find('img', alt="Icon image")
            icon = img_tag['src'] if img_tag else ''
            
            rating_tag = dsoup.find('div', itemprop="starRating")
            rating = rating_tag.text.replace("star", " ⭐️") if rating_tag else 'Unknown'
            
            app_details = f"[📲]({icon}) **{name}**\n\n"
            app_details += f"`Developer :` [{dev}]({dev_link})\n"
            app_details += f"`Rating :` {rating}\n"
            app_details += f"`Details :` [View in Play Store]({app_link})"
            
            await mg.edit(app_details, disable_web_page_preview=False)
            
    except Exception as e:
        await mg.edit(f"`Error occurred while searching:` {e}")

modules_help["app"] = {
    "app [name]": "Search for an app in the Google Play Store (defaults to India region).",
    "app -us [name]": "Search for an app in the US region (bypasses local bans)."
}
