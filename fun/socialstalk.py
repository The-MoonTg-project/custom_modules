from datetime import datetime
import json
import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
import io

from utils.misc import modules_help, prefix

TIKTOK_API_URL = "https://api.maher-zubair.tech/stalk/tiktok?q="
INSTAGRAM_API_URL = "https://tools.betabotz.eu.org/tools/stalk-ig?q="
GH_STALK = "https://api.github.com/users/"


@Client.on_message(filters.command(["tiktokstalk"], prefix) & filters.me)
async def tiktok_stalk(_, message: Message):
    query = ""
    if len(message.command) > 1:
        query = message.command[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text.strip()

    if not query:
        await message.edit(
            "Usage: `tiktokstalk <username>` or reply to a message containing the username."
        )
        return

    await message.edit("Fetching TikTok profile...")
    url = f"{TIKTOK_API_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("result", {})
        if data:
            profile_pic_url = data.get("profile", "")
            profile_pic = requests.get(profile_pic_url).content
            profile_pic_stream = io.BytesIO(profile_pic)
            profile_pic_stream.name = "profile.jpg"

            await message.reply_photo(
                photo=profile_pic_stream,
                caption=(
                    f"</b>TikTok Profile:</b>\n"
                    f"</b>Name:</b> {data.get('name', 'N/A')}\n"
                    f"</b>Username:</b> {data.get('username', 'N/A')}\n"
                    f"</b>Followers:</b> {data.get('followers', 'N/A')}\n"
                    f"</b>Following:</b> {data.get('following', 'N/A')}\n"
                    f"</b>Likes:</b> {data.get('likes', 'N/A')}\n"
                    f"</b>Description:</b> {data.get('desc', 'N/A')}\n"
                    f"</b>Bio:</b> {data.get('bio', 'N/A')}"
                ),
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        else:
            await message.edit("No data found for this TikTok user.")
        await message.delete()
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command("ipinfo", prefix) & filters.me)
async def ipinfo(_, message: Message):
    searchip = message.text.split(" ", 1)
    if len(searchip) == 1:
        await message.edit_text(f"Usage:{prefix}ipinfo [ip]")
        return
    searchip = searchip[1]
    m = await message.edit_text("Searching...")
    await m.edit_text("🔎")
    try:
        url = requests.get(
            f"http://ip-api.com/json/{searchip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
        )
        response = json.loads(url.text)
        text = f"""
<b>IP Address:</b> <code>{response['query']}</code>
<b>Status:</b> <code>{response['status']}</code>
<b>Continent Code:</b> <code>{response['continentCode']}</code>
<b>Country:</b> <code>{response['country']}</code>
<b>Country Code :</b> <code>{response['countryCode']}</code>
<b>Region:</b> <code>{response['region']}</code>
<b>Region Name :</b> <code>{response['regionName']}</code>
<b>City:</b> <code>{response['city']}</code>
<b>District:</b> <code>{response['district']}</code>
<b>ZIP:</b> <code>{response['zip']}</code>
<b>Latitude:</b> <code>{response['lat']}</code>
<b>Longitude:</b> <code>{response['lon']}</code>
<b>Time Zone:</b> <code>{response['timezone']}</code>
<b>Offset:</b> <code>{response['offset']}</code>
<b>Currency:</b> <code>{response['currency']}</code>
<b>ISP:</b> <code>{response['isp']}</code>
<b>Org:</b> <code>{response['org']}</code>
<b>As:</b> <code>{response['as']}</code>
<b>Asname:</b> <code>{response['asname']}</code>
<b>Reverse:</b> <code>{response['reverse']}</code>
<b>User is on Mobile:</b> <code>{response['mobile']}</code>
<b>Proxy:</b> <code>{response['proxy']}</code>
<b>Hosting:</b> <code>{response['hosting']}</code>"""
        await m.edit_text(text)
    except:
        await m.edit_text("Unable To Find Info!")


@Client.on_message(filters.command("instastalk", prefix) & filters.me)
async def instagram_stalk(_, message: Message):
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text
    else:
        await message.edit(
            f"Usage: <code>{prefix}instastalk <username></code> or reply to a message containing the username."
        )
        return

    await message.edit("Fetching Instagram profile...")
    url = f"{INSTAGRAM_API_URL}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("result", {}).get("user_info", {})
        if data:
            profile_pic_url = data.get("profile_pic_url", "")
            profile_pic = requests.get(profile_pic_url).content
            profile_pic_stream = io.BytesIO(profile_pic)
            profile_pic_stream.name = "profile.jpg"

            await message.reply_photo(
                photo=profile_pic_stream,
                caption=(
                    f"</b>Instagram Profile:</b>\n"
                    f"</b>Full Name:</b> {data.get('full_name', 'N/A')}\n"
                    f"</b>Username:</b> {data.get('username', 'N/A')}\n"
                    f"</b>Biography:</b> {data.get('biography', 'N/A')}\n"
                    f"</b>External URL:</b> {data.get('external_url', 'N/A')}\n"
                    f"</b>Posts:</b> {data.get('posts', 'N/A')}\n"
                    f"</b>Followers:</b> {data.get('followers', 'N/A')}\n"
                    f"</b>Following:</b> {data.get('following', 'N/A')}"
                ),
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        else:
            await message.edit("No data found for this Instagram user.")
        await message.delete()
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command("ghstalk", prefix) & filters.me)
async def github_stalk(_, message: Message):
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text
    else:
        await message.edit(
            f"Usage: <code>{prefix}ghstalk <username></code> or reply to a message containing the username."
        )
        return

    await message.edit("Fetching GitHub profile...")
    url = f"{GH_STALK}{query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        created_at = data.get("created_at", "N/A")
        formatted_date = (
            datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z")
            if created_at != "N/A"
            else None
        )
        if data:
            await message.reply_photo(
                photo=data.get("avatar_url", "").replace("?v=4", ""),
                caption=f"</b>GitHub Profile:</b>\n"
                f"</b>Name:</b> {data.get('name', 'N/A')}\n"
                f"</b>Username:</b> {data.get('login', 'N/A')}\n"
                f"</b>Bio:</b> {data.get('bio', 'N/A')}\n"
                f"</b>Public Repositories:</b> <a href='{data.get('repos_url', '')}'>{data.get('public_repos', 'N/A')}</a>\n"
                f"</b>Public Gists:</b> <a href='{data.get('gists_url', '')}'>{data.get('public_gists', 'N/A')}</a>\n"
                f"</b>Company:</b> {data.get('company', 'N/A')}\n"
                f"</b>Location:</b> {data.get('location', 'N/A')}\n"
                f"</b>Email:</b> {data.get('email', 'N/A')}\n"
                f"</b>Website:</b> {data.get('blog', 'N/A')}\n"
                f"</b>Created At:</b> {formatted_date.strftime('%Y-%m-%d %I:%M:%S %p') if formatted_date else 'N/A'}"
                f"</b>Hireable:</b> {data.get('hireable', 'N/A')}\n"
                f"</b>Followers:</b> {data.get('followers', 'N/A')}\n"
                f"</b>Following:</b> {data.get('following', 'N/A')}",
            )
        else:
            await message.edit("No data found for this GitHub user.")
    else:
        await message.edit("An error occurred, please try again later.")


modules_help["socialstalk"] = {
    "tiktokstalk [username]*": "Get TikTok profile information",
    "ipinfo [IP address]*": "Get information about an IP address",
    "instastalk [username]*": "Get Instagram profile information",
    "ghstalk [username]*": "Get GitHub profile information",
}
