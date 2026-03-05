from typing import Union

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.scripts import import_library

from utils import modules_help, prefix

bs4 = import_library("bs4", "beautifulsoup4")
from bs4 import BeautifulSoup


def get_text(message: Message) -> Union[str, None]:
    """Extract Text From Commands"""
    if message.text is None:
        return
    if " " not in message.text:
        return
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        pass


@Client.on_message(filters.command("score", prefix) & filters.me)
async def score(_, message: Message):
    score_page = "http://static.cricinfo.com/rss/livescores.xml"
    async with aiohttp.ClientSession() as session:
        async with session.get(score_page) as resp:
            page = await resp.text()
    soup = BeautifulSoup(page, "html.parser")
    result = soup.find_all("description")
    sed = "".join(match.get_text() + "\n\n" for match in result)
    await message.edit(
        f"<b>Match information:</b><u> Credits Friday team</u>\n\n\n<code>{sed}</code>",
        parse_mode=enums.ParseMode.HTML,
    )


modules_help["score"] = {"score": "get live cricket scores"}
