import requests
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix


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


modules_help["ipinfo"] = {"ipinfo [ip address]*": "ip address info"}
