import calendar
from datetime import datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from pyrogram import Client, filters
from datetime import datetime
from utils.misc import modules_help, prefix
import os
from pyrogram.errors import MessageTooLong

from PIL import Image, ImageEnhance
from io import BytesIO
import aiohttp

import requests

from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

CALENDARIFIC_API_KEY = " "


@Client.on_message(filters.command("date", prefix) & filters.me)
async def date(client, message):
    month = datetime.now().month
    year = datetime.now().year
    date = datetime.now().strftime("Date - %B %d, %Y\Time - %H:%M:%S")
    cal = calendar.month(year, month)
    await message.edit_text(f"<code>{date}\n{cal}</code>")
    
@Client.on_message(filters.command("holidays" , prefix) & filters.me)
async def get_holidays(client, message):
    try:
        country = 'IN'  # Set your desired country code here
        year = 2024  # Default year

        # Extract the year from the command if provided
        if len(message.command) > 1:
            try:
                year = int(message.command[1])
            except ValueError:
                await message.reply("Please provide a valid year.")
                return

        url = f"https://calendarific.com/api/v2/holidays?api_key={CALENDARIFIC_API_KEY}&country={country}&year={year}"
        response = requests.get(url)
        data = response.json()

        if data['meta']['code'] == 200:
            holidays = data['response']['holidays']
            message_text = f"Holidays for {year}:\n"
            for holiday in holidays:
                date = holiday['date']['iso']
                name = holiday['name']
                message_text += f"{date}: {name}\n"
            await message.reply(message_text)
        else:
            await message.reply("Failed to retrieve holidays. Please try again later.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")


EVAA = [
    [
        InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/moonub_chat"),
    ],
]

async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"code": code}) as resp:
            image_data = await resp.read()

    # Open the image using PIL
    carbon_image = Image.open(BytesIO(image_data))

    # Increase brightness
    enhancer = ImageEnhance.Brightness(carbon_image)
    bright_image = enhancer.enhance(1.7)  # Adjust the enhancement factor as needed

    # Save the modified image to BytesIO object with increased quality
    output_image = BytesIO()
    bright_image.save(output_image, format='PNG', quality=95)  # Adjust quality as needed
    output_image.name = "carbon.png"
    return output_image


@Client.on_message(filters.command("Calendar", prefix) & filters.me)
async def send_calendar(client, message):
    # Extract the year from the command arguments
    command_parts = message.text.split(" ")
    if len(command_parts) == 2:
        try:
            year = int(command_parts[1])
        except ValueError:
            await message.reply("✦ ɪɴᴠᴀʟɪᴅ ʏᴇᴀʀ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴜsᴇ {prefix}Calendar <year>")
            return
    else:
        await message.reply("✦ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ʏᴇᴀʀ ᴀғᴛᴇʀ {prefix}Calendar ᴄᴏᴍᴍᴀɴᴅ.")
        return

    # Generate the calendar for the specified year using the calendar module
    cal = calendar.TextCalendar()
    full_year_calendar = cal.formatyear(year, 2, 1, 1, 3)
    # Generate the Carbon image for the calendar
    carbon_image = await make_carbon(full_year_calendar)

    # Send the image as a reply to the user
    await message.reply_photo(photo=carbon_image, caption=f"✦ ʜᴇʀᴇ ɪs ʏᴏᴜʀ {year} ᴄᴀʟᴇɴᴅᴀʀ.", reply_markup=InlineKeyboardMarkup(EVAA),)
    



# Function to fetch history data from Muffinlabs API

def get_history_data():
    today = datetime.now().strftime("%m/%d")
    url = f"http://history.muffinlabs.com/date"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        return None

def format_history(data):
    events = data.get('Events', [])
    if not events:
        return "No events found for today."
    
    formatted_events = []
    for event in events:
        year = event.get("year", "Unknown year")
        text = event.get("text", "")
        links = event.get("links", [])
        link_text = ""
        
        # Add the first link if available
        if links:
            link_title = links[0].get("title", "")
            link_url = links[0].get("link", "")
            link_text = f"\nRead more: [{link_title}]({link_url})"
        
        formatted_events.append(f"{year}: {text}{link_text}")
    
    return "\n\n".join(formatted_events)

@Client.on_message(filters.command("history", prefix) & filters.me)
async def today_history(client, message):
    try:
        # Fetch the history data
        history_data = get_history_data()
        
        if history_data:
            # Format and send the events
            events_text = format_history(history_data)
            await message.reply(events_text, disable_web_page_preview=True)
        else:
            await message.reply("Sorry, I couldn't fetch today's history data.")
    
    except MessageTooLong:
        # Save the large response to a file
        with open("history.txt", "w") as f:
            f.write(events_text)
        
        # Prepare general details for the caption
        general_details = "Here's today's historical events."
        
        # Send the file with a caption
        await message.reply_document(
            "history.txt",
            caption=f"<u><b>General Details</b></u>:\n{general_details}",
        )
        
        # Clean up by removing the file after sending
        os.remove("history.txt")
    
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
      


    


modules_help["date"] = {
    "date": " Show Current Date and Calendar",
    "holidays": "Show Current holiday"
    "Callender": " Callender for full year"
    "history": "get the today history"
}
