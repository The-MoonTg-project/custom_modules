import re
import bs4
import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix

@Client.on_message(filters.command(["app"], prefix) & filters.me)
async def send_app(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("`Provide an app name to search.`")
        return
        
    app_name = " ".join(message.command[1:])
    gl = "IN"
    forced_us = False
        
    if not app_name:
        await message.edit("`Provide an app name to search.`")
        return
        
    mg = await message.edit(f"`Searching Play Store...`")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async def fetch_page(url):
                async with session.get(url, headers=headers) as page:
                    return await page.text()

            if forced_us or gl != "IN":
                content = await fetch_page(f"https://play.google.com/store/search?q={app_name}&c=apps&gl={gl}&hl=en")
                soup = bs4.BeautifulSoup(content, 'html.parser')
                links = soup.find_all('a', href=re.compile(r'/store/apps/details\?id='))
                if not links:
                    await mg.edit("`No apps found for this query.`")
                    return
                target_link = "https://play.google.com" + links[0]['href']
                target_gl = gl
                d_content = await fetch_page(f"{target_link}&gl={target_gl}&hl=en")
                dsoup = bs4.BeautifulSoup(d_content, 'html.parser')
            else:
                # Automatic fallback logic: search both IN and US concurrently
                in_content, us_content = await asyncio.gather(
                    fetch_page(f"https://play.google.com/store/search?q={app_name}&c=apps&gl=IN&hl=en"),
                    fetch_page(f"https://play.google.com/store/search?q={app_name}&c=apps&gl=US&hl=en")
                )
                
                in_soup = bs4.BeautifulSoup(in_content, 'html.parser')
                us_soup = bs4.BeautifulSoup(us_content, 'html.parser')
                
                in_links = in_soup.find_all('a', href=re.compile(r'/store/apps/details\?id='))
                us_links = us_soup.find_all('a', href=re.compile(r'/store/apps/details\?id='))
                
                in_link = "https://play.google.com" + in_links[0]['href'] if in_links else None
                us_link = "https://play.google.com" + us_links[0]['href'] if us_links else None
                
                if not in_link and not us_link:
                    await mg.edit("`No apps found for this query.`")
                    return
                elif in_link and us_link and in_link != us_link:
                    in_detail, us_detail = await asyncio.gather(
                        fetch_page(f"{in_link}&gl=IN&hl=en"),
                        fetch_page(f"{us_link}&gl=US&hl=en")
                    )
                    in_dsoup = bs4.BeautifulSoup(in_detail, 'html.parser')
                    us_dsoup = bs4.BeautifulSoup(us_detail, 'html.parser')
                    
                    in_name_tag = in_dsoup.find('h1', itemprop="name")
                    in_name = in_name_tag.text if in_name_tag else in_dsoup.h1.text if in_dsoup.h1 else ""
                    
                    us_name_tag = us_dsoup.find('h1', itemprop="name")
                    us_name = us_name_tag.text if us_name_tag else us_dsoup.h1.text if us_dsoup.h1 else ""
                    
                    query_lower = app_name.lower()
                    in_match = query_lower in in_name.lower()
                    us_match = query_lower in us_name.lower()
                    
                    # If US matches the query but IN does not (e.g., TikTok vs Tikio Guide)
                    if us_match and not in_match:
                        target_link, target_gl, dsoup = us_link, "US", us_dsoup
                    else:
                        target_link, target_gl, dsoup = in_link, "IN", in_dsoup
                else:
                    target_link = in_link or us_link
                    target_gl = "IN" if in_link else "US"
                    d_content = await fetch_page(f"{target_link}&gl={target_gl}&hl=en")
                    dsoup = bs4.BeautifulSoup(d_content, 'html.parser')

            name_tag = dsoup.find('h1', itemprop="name")
            name = name_tag.text if name_tag else dsoup.h1.text if dsoup.h1 else 'Unknown'
            
            dev_tag = dsoup.find('a', href=re.compile(r'/store/apps/dev\?id=|/store/apps/developer\?id='))
            dev = dev_tag.text if dev_tag else 'Unknown'
            dev_link = "https://play.google.com" + dev_tag['href'] if dev_tag else target_link
            
            img_tag = dsoup.find('img', alt="Icon image")
            icon = img_tag['src'] if img_tag else ''
            
            rating_tag = dsoup.find('div', itemprop="starRating")
            rating = rating_tag.text.replace("star", " ⭐️") if rating_tag else 'Unknown'
            
            app_details = f"[📲]({icon}) **{name}**\n\n"
            app_details += f"`Developer :` [{dev}]({dev_link})\n"
            app_details += f"`Rating :` {rating}\n"
            app_details += f"`Details :` [View in Play Store]({target_link})"
            
            await mg.edit(app_details, disable_web_page_preview=False)
            
    except Exception as e:
        await mg.edit(f"`Error occurred while searching:` {e}")

modules_help["app"] = {
    "app [name]": "Search for an app in the Google Play Store (auto-falls back to US store for banned apps)."
}
