from io import BytesIO
import requests

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong, MediaEmpty

from utils.scripts import format_exc
from utils.misc import prefix, modules_help
from utils.db import db

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
        response = requests.get(f"{API_URL}planetary/apod", params=params).json()
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
        response = requests.get(f"{API_URL}DONKI/notifications", params=params).json()
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
        response = requests.get(url)
        count = response.json()[0]["count(pl_name)"]
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
        response = requests.get(f"{API_URL}/planetary/earth/imagery", params=params)
        image_data = BytesIO(response.content)
        if response.status_code == 200:
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
        response = requests.get(f"{API_URL}/EPIC/api/natural", params=params).json()
        if isinstance(response, list):
            response = response[0]
        if response.get("error"):
            return await message.edit_text(response["error"]["message"])
        date = response["date"].split(" ")[0].replace("-", "/")
        image_url = f"https://api.nasa.gov/EPIC/archive/natural/{date}/png/{response['image']}.png"
        image_data = BytesIO(requests.get(image_url, params=params).content)
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


modules_help["nasa"] = {
    "apod": "Get Astronomy Picture of the Day from NASA.",
    "earthpic": "Get Earth Polychromatic Imaging Camera (EPIC) image from NASA.",
    "earthi [longitude]* [lattitude]*": "Get Earth Imagery from NASA.",
    "exoplanet": "Get Exoplanet data from NASA.",
    "donki": "Get Space Weather data from NASA.",
    "nasa_api [api_key]*": "Set your NASA API key to use the commands.",
}
