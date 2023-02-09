from pyrogram import Client, filters
from pyrogram.types import Message
from requests import get

from utils.misc import modules_help, prefix
from utils.scripts import import_library

bs4 = import_library("bs4", "beautifulsoup4")
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/80.0.3987.149 Safari/537.36"
}


@Client.on_message(filters.command(["vk_profile", "vk"], prefix) & filters.me)
async def vk_profile(_, message: Message):
    await message.edit("<b>Fetching info...</b>")
    response = get(f"https://vk.com/{message.command[1]}", headers=headers, timeout=3)
    soup = BeautifulSoup(response.text, "html.parser")
    name = f"Name and surname: {soup.find('h1', class_='page_name')}"
    if soup.find("h5", class_="profile_deleted_text"):
        text = f"{name}\n\nProfile is only available for authorized users"
    else:
        text = name
        for item in soup.find_all("div", class_="clear_fix profile_info_row"):
            text += str(item)
    await message.edit(text, disable_web_page_preview=True)


modules_help["vk_profile"] = {"vk": "Get open info from VK profile"}
