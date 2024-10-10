import calendar
from datetime import datetime
import requests
from pyrogram import Client, filters
from datetime import datetime
from utils.misc import modules_help, prefix
import os
from pyrogram.errors import MessageTooLong

import requests

from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import make_carbon


def get_history_data():
    today = datetime.now().strftime("%m/%d")
    url = f"http://history.muffinlabs.com/date"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
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
    date = datetime.now().strftime("Date - %B %d, %Y\Time - %H:%M:%S")
    cal = calendar.month(year, month)
    await message.edit_text(f"<code>{date}\n{cal}</code>")


# TODO: A better way to do this without 3rd party API
# @Client.on_message(filters.command("holidays", prefix) & filters.me)
# async def get_holidays(_, message: Message):
#     try:
#         country = "IN"
#         year = datetime.now().year

#         if len(message.command) > 1:
#             try:
#                 year = int(message.command[1])
#             except ValueError:
#                 await message.edit("Please provide a valid year.")
#                 return

#         url = f"https://calendarific.com/api/v2/holidays?api_key={CALENDARIFIC_API_KEY}&country={country}&year={year}"
#         response = requests.get(url)
#         data = response.json()

#         if data["meta"]["code"] == 200:
#             holidays = data["response"]["holidays"]
#             message_text = f"Holidays for {year}:\n"
#             for holiday in holidays:
#                 date = holiday["date"]["iso"]
#                 name = holiday["name"]
#                 message_text += f"{date}: {name}\n"
#             await message.edit(message_text)
#         else:
#             await message.edit("Failed to retrieve holidays. Please try again later.")
#     except Exception as e:
#         await message.edit(f"An error occurred: {str(e)}")


@Client.on_message(filters.command("calendar", prefix) & filters.me)
async def send_calendar(_, message: Message):
    command_parts = message.text.split(" ")
    if len(command_parts) == 2:
        try:
            year = int(command_parts[1])
        except ValueError:
            await message.edit(
                "✦ ɪɴᴠᴀʟɪᴅ ʏᴇᴀʀ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴜsᴇ {prefix}calendar <year>"
            )
            return
    else:
        year = datetime.now().year

    m = await message.edit("✦ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴀʟᴇɴᴅᴀʀ...")

    cal = calendar.TextCalendar()
    full_year_calendar = cal.formatyear(year, 2, 1, 1, 3)
    carbon_image = await make_carbon(full_year_calendar)

    await message.reply_photo(
        photo=carbon_image, caption=f"✦ ʜᴇʀᴇ ɪs ʏᴏᴜʀ {year} ᴄᴀʟᴇɴᴅᴀʀ."
    )
    if os.path.exists("carbon.png"):
        os.remove("carbon.png")
    await m.delete()


@Client.on_message(filters.command("history", prefix) & filters.me)
async def today_history(client, message: Message):
    try:
        history_data = get_history_data()

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
    # "holidays": "Show Current holiday",
    "calender": " Calender for full year",
    "history": "get the today history",
}
