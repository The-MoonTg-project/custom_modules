import os
import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# Space-Track.org credentials
SPACETRACK_USER = ""  # Your Space-Track username
SPACETRACK_PASS = ""  # Your Space-Track password


# Function to login to Space-Track.org and get an authentication session
def space_track_login():
    """Establishes a session with Space-Track.org"""
    session = requests.Session()
    login_url = "https://www.space-track.org/ajaxauth/login"
    data = {
        "identity": SPACETRACK_USER,
        "password": SPACETRACK_PASS,
    }
    response = session.post(login_url, data=data)
    if response.status_code == 200:
        return session
    return None


# Function to fetch satellite details from Space-Track.org
def fetch_satellite_data(satellite_id):
    """Fetches satellite data from Space-Track.org"""
    session = space_track_login()
    if not session:
        return None

    query_url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{satellite_id}/orderby/epoch desc/limit/1/format/json"
    response = session.get(query_url)

    if response.status_code == 200:
        return response.json()[0]  # Return the latest TLE data
    return None


# Function for live tracking (returns satellite position over time)


# Command to get satellite data (TLE data, launch date, etc.)
@Client.on_message(filters.command("satellite", prefix) & filters.me)
async def get_satellite_info(client, message):
    """Handles the 'satellite' command"""
    if len(message.command) < 2:
        await message.edit_text("Please provide a satellite ID.")
        return

    satellite_id = message.command[1]
    await message.edit_text("Fetching satellite data...")
    data = fetch_satellite_data(satellite_id)

    if data:
        # Format the response using HTML
        info = f"""
        <b>Satellite Details:</b>
        <b>Name:</b> <code>{data['OBJECT_NAME']}</code>
        <b>NORAD ID:</b> <code>{data['NORAD_CAT_ID']}</code>
        <b>Epoch Time:</b> <code>{data['EPOCH']}</code>
        <b>Inclination:</b> <code>{data['INCLINATION']}°</code>
        <b>Right Ascension:</b> <code>{data['RA_OF_ASC_NODE']}°</code>
        <b>Eccentricity:</b> <code>{data['ECCENTRICITY']}</code>
        <b>Orbital Period:</b> <code>{data['MEAN_MOTION']}</code>
        """
        await message.edit_text(info)
    else:
        await message.edit_text("Satellite data not found.")


modules_help["satellite"] = {
    "satellite [id]": "get satellite details like .satellite 60454 "
}
