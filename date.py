import calendar
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix


@Client.on_message(filters.command("date", prefix) & filters.me)
async def date(client, message):
    month = datetime.now().month
    year = datetime.now().year
    date = datetime.now().strftime("Date - %B %d, %Y\Time - %H:%M:%S")
    cal = calendar.month(year, month)
    await message.edit_text(f"<code>{date}\n{cal}</code>")


modules_help["date"] = {
    "date": " Show Current Date and Calendar",
}
