import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
import io

from utils.misc import modules_help, prefix

TIKTOK_API_URL = "https://api.maher-zubair.tech/stalk/tiktok?q="
IP_API_URL = "https://api.maher-zubair.tech/stalk/ip?q="
INSTAGRAM_API_URL = "https://tools.betabotz.eu.org/tools/stalk-ig?q="

@Client.on_message(filters.command(["tiktokstalk"], prefix) & filters.me)
async def tiktok_stalk(client, message: Message):
    query = ""
    if len(message.command) > 1:
        query = message.command[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text.strip()
    
    if not query:
        await message.edit("Usage: `tiktokstalk <username>` or reply to a message containing the username.")
        return

    await message.edit("Fetching TikTok profile...")
    url = f"{TIKTOK_API_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get('result', {})
        if data:
            profile_pic_url = data.get('profile', '')
            profile_pic = requests.get(profile_pic_url).content
            profile_pic_stream = io.BytesIO(profile_pic)
            profile_pic_stream.name = "profile.jpg"
            
            await message.reply_photo(
                photo=profile_pic_stream,
                caption=(
                    f"**TikTok Profile:**\n"
                    f"**Name:** {data.get('name', 'N/A')}\n"
                    f"**Username:** {data.get('username', 'N/A')}\n"
                    f"**Followers:** {data.get('followers', 'N/A')}\n"
                    f"**Following:** {data.get('following', 'N/A')}\n"
                    f"**Likes:** {data.get('likes', 'N/A')}\n"
                    f"**Description:** {data.get('desc', 'N/A')}\n"
                    f"**Bio:** {data.get('bio', 'N/A')}"
                ),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit("No data found for this TikTok user.")
        await message.delete()
    else:
        await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["ipinfo"], prefix) & filters.me)
async def ip_info(client, message: Message):
    query = ""
    if len(message.command) > 1:
        query = message.command[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text.strip()
    
    if not query:
        await message.edit("Usage: `ipinfo <IP address>` or reply to a message containing the IP address.")
        return

    await message.edit("Fetching IP information...")
    url = f"{IP_API_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get('result', {})
        if data.get('status') == "success":
            await message.edit(
                f"**IP Information:**\n"
                f"**IP:** {data.get('ip', 'N/A')}\n"
                f"**Continent:** {data.get('continent', 'N/A')}\n"
                f"**Country:** {data.get('country', 'N/A')}\n"
                f"**Region:** {data.get('regionName', 'N/A')}\n"
                f"**City:** {data.get('city', 'N/A')}\n"
                f"**ZIP:** {data.get('zip', 'N/A')}\n"
                f"**Latitude:** {data.get('lat', 'N/A')}\n"
                f"**Longitude:** {data.get('lon', 'N/A')}\n"
                f"**Timezone:** {data.get('timezone', 'N/A')}\n"
                f"**Currency:** {data.get('currency', 'N/A')}\n"
                f"**ISP:** {data.get('isp', 'N/A')}\n"
                f"**Organization:** {data.get('org', 'N/A')}\n"
                f"**Reverse DNS:** {data.get('reverse', 'N/A')}\n"
                f"**Mobile:** {data.get('mobile', 'N/A')}\n"
                f"**Proxy:** {data.get('proxy', 'N/A')}\n"
                f"**Hosting:** {data.get('hosting', 'N/A')}\n"
                f"**Cached:** {data.get('cached', 'N/A')}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit("Failed to fetch IP information. Please check the IP address and try again.")
    else:
        await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["instastalk"], prefix) & filters.me)
async def instagram_stalk(client, message: Message):
    query = ""
    if len(message.command) > 1:
        query = message.command[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text.strip()
    
    if not query:
        await message.edit("Usage: `instastalk <username>` or reply to a message containing the username.")
        return

    await message.edit("Fetching Instagram profile...")
    url = f"{INSTAGRAM_API_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get('result', {}).get('user_info', {})
        if data:
            profile_pic_url = data.get('profile_pic_url', '')
            profile_pic = requests.get(profile_pic_url).content
            profile_pic_stream = io.BytesIO(profile_pic)
            profile_pic_stream.name = "profile.jpg"
            
            await message.reply_photo(
                photo=profile_pic_stream,
                caption=(
                    f"**Instagram Profile:**\n"
                    f"**Full Name:** {data.get('full_name', 'N/A')}\n"
                    f"**Username:** {data.get('username', 'N/A')}\n"
                    f"**Biography:** {data.get('biography', 'N/A')}\n"
                    f"**External URL:** {data.get('external_url', 'N/A')}\n"
                    f"**Posts:** {data.get('posts', 'N/A')}\n"
                    f"**Followers:** {data.get('followers', 'N/A')}\n"
                    f"**Following:** {data.get('following', 'N/A')}"
                ),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit("No data found for this Instagram user.")
        await message.delete()
    else:
        await message.edit("An error occurred, please try again later.")

modules_help["socialstalk"] = {
    "tiktokstalk [username]*": "Get TikTok profile information",
    "ipinfo [IP address]*": "Get information about an IP address",
    "instastalk [username]*": "Get Instagram profile information",
                                           }
