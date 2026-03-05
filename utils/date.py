import calendar
import os
from datetime import datetime

import aiohttp
from pyrogram import Client, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from utils import modules_help, prefix


async def get_history_data():
    today = datetime.now().strftime("%m/%d")
    url = f"http://history.muffinlabs.com/date"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["data"]
            else:
                return None


def format_history(data):
    events = data.get("Events", [])
    if not events:
        return "No events found for today."

    formatted_events = []
    for event in events:
        year = event.get("year", "Unknown year")
        text = event.get("text", "")
        links = event.get("links", [])
        link_text = ""

        if links:
            link_title = links[0].get("title", "")
            link_url = links[0].get("link", "")
            link_text = f"\nRead more: [{link_title}]({link_url})"

        formatted_events.append(f"{year}: {text}{link_text}")

    return "\n\n".join(formatted_events)


@Client.on_message(filters.command("date", prefix) & filters.me)
async def date(_, message: Message):
    month = datetime.now().month
    year = datetime.now().year
    date = datetime.now().strftime("Date - %B %d, %Y\\Time - %H:%M:%S")
    cal = calendar.month(year, month)
    await message.edit_text(f"<code>{date}\n{cal}</code>")


@Client.on_message(filters.command("history", prefix) & filters.me)
async def today_history(client, message: Message):
    try:
        history_data = await get_history_data()

        if history_data:
            events_text = format_history(history_data)
            await message.edit(events_text, disable_web_page_preview=True)
        else:
            await message.edit("Sorry, I couldn't fetch today's history data.")

    except MessageTooLong:
        with open("history.txt", "w") as f:
            f.write(events_text)

        general_details = "Here's today's historical events."

        await message.reply_document(
            "history.txt",
            caption=f"<u><b>General Details</b></u>:\n{general_details}",
        )

        os.remove("history.txt")

    except Exception as e:
        await message.edit(f"An error occurred: {str(e)}")


modules_help["date"] = {
    "date": " Show Current Date and Calendar",
    "history": "get the today history",
}
