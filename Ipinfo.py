import requests
import json
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from functools import partial
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client as Ntbot

command = partial(filters.command, prefixes=["!", "/", "."])


@Ntbot.on_message(command("ipinfo"))
async def ipinfo(_, message: Message):
    searchip = message.text.split(" ", 1)
    if len(searchip) == 1:
        await message.reply_text("Usage:\n/ipinfo [ip]")
        return
    else:
        searchip = searchip[1]
        m = await message.reply_text("Searching...")
    try:
        url = requests.get(f"http://ip-api.com/json/{searchip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query")
        response = json.loads(url.text)
        text = f"""
IP Address: {response['query']}
Status: {response['status']}
Continent Code: {response['continentCode']}
Country: {response['country']}
Country Code : {response['countryCode']}
Region: {response['region']}
Region Name : {response['regionName']}
City: {response['city']}
District: {response['district']}
ZIP: {response['zip']}
Latitude: {response['lat']}
Longitude: {response['lon']}
Time Zone: {response['timezone']}
Offset: {response['offset']}
Currency: {response['currency']}
ISP: {response['isp']}
Org: {response['org']}
As: {response['as']}
Asname: {response['asname']}
Reverse: {response['reverse']}
User is on Mobile: {response['mobile']}
Proxy: {response['proxy']}
Hosting: {response['hosting']}"""
        await m.edit_text(text, parse_mode=enums.ParseMode.HTML)
    except:
        await m.edit_text("Unable To Find Info!")
