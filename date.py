import calendar
from datetime import datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
    



modules_help["date"] = {
    "date": " Show Current Date and Calendar",
    "holidays": "Show Current holiday"
    "Callender": " Callender for full year"
}
