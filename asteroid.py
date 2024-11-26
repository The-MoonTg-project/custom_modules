import os
import requests
from datetime import datetime, timedelta
from datetime import datetime
from pyrogram import Client, filters, enums
from datetime import datetime
from pyrogram.errors import MessageTooLong

from utils.misc import modules_help, prefix



NASA_API_KEY = " "

# Initialize the Pyrogram Client

# NASA NEO API URL
NASA_NEO_BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"

# Function to get asteroid information from NASA NEO API
def get_asteroid_info(start_date, end_date):
    url = f"{NASA_NEO_BASE_URL}?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        element_count = data['element_count']
        near_earth_objects = data['near_earth_objects']
        
        if element_count == 0:
            return "❌ No asteroids found for the given date range."

        info = f"Asteroids from {start_date} to {end_date} 🌌:\n\n"
        for date in near_earth_objects:
            for asteroid in near_earth_objects[date]:
                info += f"**🚀 {asteroid['name']}**\n"
                info += f"  - *📏 Diameter (meters):* {asteroid['estimated_diameter']['meters']['estimated_diameter_min']:.2f} - {asteroid['estimated_diameter']['meters']['estimated_diameter_max']:.2f}\n"
                info += f"  - *⚠️ Hazardous:* {'Yes' if asteroid['is_potentially_hazardous_asteroid'] else 'No'}\n"
                info += f"  - *📅 Close Approach Date:* {asteroid['close_approach_data'][0]['close_approach_date']}\n"
                info += f"  - *🌍 Miss Distance (km):* {float(asteroid['close_approach_data'][0]['miss_distance']['kilometers']):,.2f}\n"
                info += f"  - *💨 Relative Velocity (km/h):* {float(asteroid['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']):,.2f}\n\n"

        return info
    else:
        return "⚠️ Error fetching asteroid information. Please try again later."



@Client.on_message(filters.command("asteroid", prefix) & filters.me)
async def asteroids_handler(client, message):
    try:
        _, start_date, end_date = message.command
    except ValueError:
        await message.reply_text("Please provide a start and end date in the format:{prefix}asteroids YYYY-MM-DD YYYY-MM-DD")
        return

    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        await message.reply_text("Invalid date format. Please use YYYY-MM-DD.")
        return

    info = get_asteroid_info(start_date, end_date)
    try:
        await message.reply_text(info, parse_mode=enums.ParseMode.MARKDOWN)
    except MessageTooLong:
        with open("asteroid.txt", "w") as f:
            f.write(info)
        await message.reply_document(
            "asteroid.txt",
            caption=f"General Details of asteroid",
        )
        os.remove("asteroid.txt")


modules_help["asteroid"] = {
    "asteroid": "get asteroid information",
}
