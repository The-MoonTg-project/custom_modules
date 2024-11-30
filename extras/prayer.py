from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from datetime import datetime

from utils.misc import modules_help, prefix

# Aladhan API credentials
ALADHAN_API_URL = "https://api.aladhan.com/v1/timingsByCity"
DEFAULT_METHOD = 2  # Islamic Society of North America
DEFAULT_CITY = "Lahore"
DEFAULT_COUNTRY = "PK"


async def fetch_namaz_times(city_name: str, country_name: str) -> dict:
    params = {"city": city_name, "country": country_name, "method": DEFAULT_METHOD}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(ALADHAN_API_URL, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            return {"error": str(e)}


def format_time_12hr(time_str: str) -> str:
    try:
        # Split time into hours and minutes
        hours, minutes = map(int, time_str.split(":"))
        # Convert to 12-hour format
        period = "AM" if hours < 12 else "PM"
        if hours == 0:
            hours = 12
        elif hours > 12:
            hours -= 12
        elif hours == 12:
            period = "PM"
        return f"{hours}:{minutes:02d} {period}"
    except Exception as e:
        return f"Error formatting time: {str(e)}"


@Client.on_message(filters.command("prayer", prefix) & filters.me)
async def namaz_times(client: Client, message: Message):
    if message.reply_to_message:
        city_name = message.reply_to_message.text
        country_name = DEFAULT_COUNTRY  # Default to Pakistan if no country is provided
    else:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            city_name = DEFAULT_CITY
            country_name = DEFAULT_COUNTRY
        elif len(args) == 2:
            city_name = args[1]
            country_name = DEFAULT_COUNTRY
        else:
            city_name = args[1]
            country_name = args[2]

    data = await fetch_namaz_times(city_name, country_name)

    if "error" in data:
        result = f"<b>Error:</b> <i>{data['error']}</i>"
    elif "data" in data:
        timings = data["data"]["timings"]
        today = datetime.now().strftime("%Y-%m-%d")
        formatted_timings = {
            "Fajr": format_time_12hr(timings["Fajr"]),
            "Dhuhr": format_time_12hr(timings["Dhuhr"]),
            "Asr": format_time_12hr(timings["Asr"]),
            "Maghrib": format_time_12hr(timings["Maghrib"]),
            "Isha": format_time_12hr(timings["Isha"]),
        }
        result = (
            f"<b>Prayer Times for {city_name}, {country_name} on {today}:</b>\n\n"
            f"<b>Fajr:</b> {formatted_timings['Fajr']}\n"
            f"<b>Dhuhr:</b> {formatted_timings['Dhuhr']}\n"
            f"<b>Asr:</b> {formatted_timings['Asr']}\n"
            f"<b>Maghrib:</b> {formatted_timings['Maghrib']}\n"
            f"<b>Isha:</b> {formatted_timings['Isha']}\n"
        )
    else:
        result = "<b>Error:</b> <i>Unable to get prayer times for the specified location.</i>"

    await message.edit_text(result)


modules_help["namaz"] = {
    "prayer [city_name] [country_name]": "Shows the prayer times. Default to Pakistan if no country is provided"
}
