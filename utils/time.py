from pyrogram import Client, filters, enums
from pyrogram.types import Message
import aiohttp
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.misc import modules_help, prefix
from utils.scripts import import_library
from utils.db import db

pytz = import_library("pytz")


async def fetch_json(url: str, params: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            return {"error": str(e)}


async def get_coordinates(GEO_API_USERNAME, city_name: str):
    search_url = "http://api.geonames.org/searchJSON"
    params = {"q": city_name, "username": GEO_API_USERNAME, "maxRows": 1}
    data = await fetch_json(search_url, params)
    if "geonames" in data and data["geonames"]:
        return data["geonames"][0]["lat"], data["geonames"][0]["lng"]
    return None, None


async def get_city_time_with_api(city_name: str) -> str:
    GEO_API_USERNAME = db.get("custom.geoapi", "api", None)
    if GEO_API_USERNAME is None:
        return "<b>Error:</b> <i>GeoNames API credentials not provided.</i>"
    lat, lng = await get_coordinates(city_name)
    if lat is None or lng is None:
        return "<b>Error:</b> <i>City not found or invalid city name.</i>"

    time_url = "http://api.geonames.org/timezoneJSON"
    params = {"username": GEO_API_USERNAME, "lat": lat, "lng": lng}
    data = await fetch_json(time_url, params)
    if "timezoneId" in data:
        timezone = ZoneInfo(data["timezoneId"])
        city_time = datetime.now(timezone)
        local_time = city_time.strftime("%Y-%m-%d %I:%M:%S %p")
        weekday = city_time.strftime("%A")
        return (
            f"<b>Current Time in {city_name}:</b>\n"
            f"<i>Local Time:</i> {local_time}\n"
            f"<i>Weekday:</i> {weekday}\n"
            f"<i>Time Zone:</i> {data['timezoneId']}"
        )
    return "<b>Error:</b> <i>Unable to get time for the specified coordinates.</i>"


def get_city_time(country_name: str) -> str:
    try:
        countries = pytz.country_names
        for country in countries:
            if countries[country].lower() == country_name.lower():
                zone = pytz.country_timezones[country][0]
                timezone = pytz.timezone(zone)
                city_time = datetime.now(timezone)
                local_time = city_time.strftime("%Y-%m-%d %I:%M:%S %p")
                weekday = city_time.strftime("%A")
                return (
                    f"<b>Current Time in {country_name}:</b>\n"
                    f"<b>Local Time:</b> <code>{local_time}</code>\n"
                    f"<b>Weekday:</b> <code>{weekday}</code>\n"
                    f"<b>Time Zone:</b> <code>{zone}</code>"
                )
    except pytz.UnknownTimeZoneError:
        return "Error: Unable to get time for the specified country."


@Client.on_message(filters.command("timeapi", prefix) & filters.me)
async def city_time(_, message: Message):
    if message.reply_to_message:
        city_name = message.reply_to_message.text
    else:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            result = "<b>Please provide a city name.</b>"
            await message.edit(result)
            return
        city_name = args[1]

    result = await get_city_time_with_api(city_name)
    await message.edit(result)


@Client.on_message(filters.command("time", prefix) & filters.me)
async def time(_, message: Message):
    if message.reply_to_message:
        city_name = message.reply_to_message.text
    else:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            result = "<b>Please provide a country name.</b>"
            await message.edit(result)
            return
        city_name = args[1]

    result = get_city_time(city_name)
    await message.edit(result)


@Client.on_message(filters.command("set_geoapi", prefix) & filters.me)
async def set_geoapi(_, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        result = "<b>Please provide the GeoNames API credentials.</b>"
    else:
        api_key = args[1]
        db.set("custom.geoapi", "api", api_key)
        result = "<b>GeoNames API credentials set successfully.</b>"
    await message.edit(result)


modules_help["time"] = {
    "timeapi [city_name]": "Shows current time for the specified city using GeoNames API.",
    "time [country_name]": "Shows current time for the specified country using pytz library.",
}
