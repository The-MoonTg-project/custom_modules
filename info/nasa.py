import os
from datetime import datetime
from io import BytesIO

import aiohttp
from pyrogram import Client, filters
from pyrogram.errors import MediaEmpty, MessageTooLong
from pyrogram.types import Message
from utils.db import db
from utils.scripts import format_exc

from utils import modules_help, prefix

API_URL = "https://api.nasa.gov/"


@Client.on_message(filters.command("apod", prefix) & filters.me)
async def nasa_apod(client: Client, message: Message):
    api_key = db.get("custom.nasa", "api", None)
    if not api_key:
        await message.edit_text(
            "API Key isn't set using dmeo key instead, it has much lower rate limits!"
        )
    try:
        await message.edit_text("Getting APOD...")
        params = {
            "api_key": api_key if api_key else "DEMO_KEY",
            "thumbs": True,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}planetary/apod", params=params) as resp:
                response = await resp.json()
    except Exception as e:
        return await message.edit_text(format_exc(e))
    if response.get("error"):
        return await message.edit_text(response["error"]["message"])
    caption = f"<b>Title:</b> {response['title']}\n<b>Date:</b> {response['date']}\n\n<b>Explanation:</b> {response['explanation']}"
    await message.delete()
    await client.send_photo(
        message.chat.id,
        photo=response["thumbnail_url"]
        if response["media_type"] == "video"
        else response["url"],
        caption=caption,
        reply_to_message_id=message.reply_to_message_id,
    )


@Client.on_message(filters.command("donki", prefix) & filters.me)
async def nasa_donki(_, message: Message):
    api_key = db.get("custom.nasa", "api", None)
    if not api_key:
        await message.edit_text(
            "API Key isn't set using dmeo key instead, it has much lower rate limits!"
        )
    try:
        await message.edit_text("Getting latest notification...")
        params = {
            "api_key": api_key if api_key else "DEMO_KEY",
            "type": "all",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}DONKI/notifications", params=params
            ) as resp:
                response = await resp.json()
        print(response)
        if isinstance(response, list):
            response = response[0]
        if response.get("error"):
            return await message.edit_text(response["error"]["message"])
        msg = f"<b>Type:</b> {response['messageType']}\n<b>Date:</b> {response['messageIssueTime']}"
        body = f"\n<b>Details:</b> {response['messageBody']}"
        await message.edit_text(msg + body)
    except MessageTooLong:
        msg += f"\n<b>Details:</b> <a href='{response['messageURL']}'>Click Here</a>"
        await message.edit_text(msg)
    except Exception as e:
        return await message.edit_text(format_exc(e))


@Client.on_message(filters.command("exoplanet", prefix) & filters.me)
async def nasa_exoplanet(_, message: Message):
    try:
        await message.edit_text("Fetching number of exoplanets...")
        url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+count(pl_name)+from+ps+where+default_flag=1&format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        count = data[0]["count(pl_name)"]
        await message.edit_text(f"There are {count} confirmed exoplanets!")
    except Exception as e:
        return await message.edit_text(format_exc(e))


@Client.on_message(filters.command("earthi", prefix) & filters.me)
async def nasa_earthi(client: Client, message: Message):
    api_key = db.get("custom.nasa", "api", None)
    if not api_key:
        await message.edit_text(
            "API Key isn't set using dmeo key instead, it has much lower rate limits!"
        )
    if len(message.command) < 3:
        return await message.edit_text("Please provide a longitude & lattitude!")
    elif "." not in message.command[1] or "." not in message.command[2]:
        return await message.edit_text("Please provide a valid longitude & lattitude!")
    lon = message.text.split(maxsplit=2)[1]
    lat = message.text.split(maxsplit=2)[2]
    try:
        await message.edit_text("Getting image...")
        params = {
            "api_key": api_key if api_key else "DEMO_KEY",
            "dim": "0.15",
            "lon": lon,
            "lat": lat,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/planetary/earth/imagery", params=params
            ) as resp:
                image_data = BytesIO(await resp.read())
                if resp.status == 200:
                    await client.send_photo(
                        message.chat.id,
                        photo=image_data,
                        reply_to_message_id=message.reply_to_message_id,
                    )
    except MediaEmpty:
        await message.edit_text("No imagery for specified date!")
    except Exception as e:
        return await message.edit_text(format_exc(e))
    finally:
        await message.delete()


@Client.on_message(filters.command("earthpic", prefix) & filters.me)
async def nasa_earthpic(client: Client, message: Message):
    api_key = db.get("custom.nasa", "api", None)
    if not api_key:
        await message.edit_text(
            "API Key isn't set using dmeo key instead, it has much lower rate limits!"
        )
    try:
        await message.edit_text("Getting image...")
        params = {
            "api_key": api_key if api_key else "DEMO_KEY",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/EPIC/api/natural", params=params
            ) as resp:
                response = await resp.json()
            if isinstance(response, list):
                response = response[0]
            if response.get("error"):
                return await message.edit_text(response["error"]["message"])
            date = response["date"].split(" ")[0].replace("-", "/")
            image_url = f"https://api.nasa.gov/EPIC/archive/natural/{date}/png/{response['image']}.png"
            async with session.get(image_url, params=params) as resp:
                image_data = BytesIO(await resp.read())
        caption = (
            f"<b>Date:</b> {response['date']}\n<b>Caption:</b> {response['caption']}"
        )
        if response.get("centroid_coordinates"):
            centroid_coordinates = response["centroid_coordinates"]
            caption += f"\n<b>Centroid Coordinates:</b> Latitude: {centroid_coordinates['lat']}, Longitude: {centroid_coordinates['lon']}"
        if response.get("dscovr_j2000_position"):
            dscovr_j2000_position = response["dscovr_j2000_position"]
            caption += f"\n<b>DSCOVR Position:</b> X: {dscovr_j2000_position['x']}, Y: {dscovr_j2000_position['y']}, Z: {dscovr_j2000_position['z']}"
        if response.get("lunar_j2000_position"):
            lunar_j2000_position = response["lunar_j2000_position"]
            caption += f"\n<b>Lunar Position:</b> X: {lunar_j2000_position['x']}, Y: {lunar_j2000_position['y']}, Z: {lunar_j2000_position['z']}"
        if response.get("sun_j2000_position"):
            sun_j2000_position = response["sun_j2000_position"]
            caption += f"\n<b>Sun Position:</b> X: {sun_j2000_position['x']}, Y: {sun_j2000_position['y']}, Z: {sun_j2000_position['z']}"
        if response.get("attitude_quaternions"):
            attitude_quaternions = response["attitude_quaternions"]
            caption += f"\n<b>Attitude Quaternions:</b> Q0: {attitude_quaternions['q0']}, Q1: {attitude_quaternions['q1']}, Q2: {attitude_quaternions['q2']}, Q3: {attitude_quaternions['q3']}"
        if response.get("coords"):
            coords = response["coords"]
            caption += f"\n<b>Coords:</b> Centroid Coordinates: Latitude: {coords['centroid_coordinates']['lat']}, Longitude: {coords['centroid_coordinates']['lon']}, Dscovr Position: X: {coords['dscovr_j2000_position']['x']}, Y: {coords['dscovr_j2000_position']['y']}, Z: {coords['dscovr_j2000_position']['z']}, etc."
        await client.send_photo(
            message.chat.id,
            photo=image_data,
            caption=caption,
            reply_to_message_id=message.reply_to_message_id,
        )
    except MediaEmpty:
        await message.edit_text("No imagery for specified date!")
    except Exception as e:
        return await message.edit_text(format_exc(e))
    finally:
        await message.delete()


@Client.on_message(filters.command("nasa_api", prefix) & filters.me)
async def nasa_api(_, message: Message):
    nasa_api = db.get("custom.nasa", "api", None)
    if len(message.command) == 1:
        return await message.edit_text("Please provide api key to set!")
    api_key = message.text.split(maxsplit=1)[1]
    if not nasa_api:
        db.set("custom.nasa", "api", api_key)
    else:
        db.remove("custom.nasa", "api")
        db.set("custom.nasa", "api", api_key)
    await message.edit_text("Nasa api key set successfully!")


@Client.on_message(filters.command("asteroids", prefix) & filters.me)
async def asteroids_handler(_, message: Message):
    api_key = db.get("custom.nasa", "api", None)
    if not api_key:
        await message.edit_text(
            "API Key isn't set using dmeo key instead, it has much lower rate limits!"
        )
    try:
        _, start_date, end_date = message.command
    except ValueError:
        await message.edit_text(
            f"Please provide a start and end date in the format:{prefix}asteroids YYYY-MM-DD YYYY-MM-DD"
        )
        return

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        await message.edit_text("Invalid date format. Please use YYYY-MM-DD.")
        return

    url = f"{API_URL}neo/rest/v1/feed"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "api_key": api_key if api_key else "DEMO_KEY",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                element_count = data["element_count"]
                near_earth_objects = data["near_earth_objects"]

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

                with open("asteroids.txt", "w") as f:
                    f.write(info)
                await message.reply_document(
                    "asteroids.txt",
                    caption=f"Asteroids from {start_date} to {end_date} 🌌:",
                )
                os.remove("asteroids.txt")
                return
            else:
                return await message.edit_text(
                    "⚠️ Error fetching asteroid information. Please try again later."
                )


modules_help["nasa"] = {
    "apod": "Get Astronomy Picture of the Day from NASA.",
    "earthpic": "Get Earth Polychromatic Imaging Camera (EPIC) image from NASA.",
    "earthi [longitude]* [lattitude]*": "Get Earth Imagery from NASA.",
    "exoplanet": "Get Exoplanet data from NASA.",
    "donki": "Get Space Weather data from NASA.",
    "asteroids [start_date]* [end_date]*": "Get Asteroid data from NASA.",
    "nasa_api [api_key]*": "Set your NASA API key to use the commands.",
}
