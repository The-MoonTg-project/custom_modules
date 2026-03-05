import re

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.scripts import import_library

from utils import modules_help, prefix

bs4 = import_library("bs4", "beautifulsoup4")
from bs4 import BeautifulSoup


@Client.on_message(filters.command("specs", prefix) & filters.me)
async def devices_specifications(_, message):
    """Mobile devices specifications"""
    textx = message.reply_to_message
    brand = (
        message.text.split(" ")[1].lower() if len(message.text.split(" ")) > 1 else ""
    )
    device = (
        " ".join(message.text.split(" ")[2:]).lower()
        if len(message.text.split(" ")) > 2
        else ""
    )
    if brand and device:
        pass
    elif textx:
        brand = textx.text.split(" ")[0]
        device = " ".join(textx.text.split(" ")[1:])
    else:
        await message.edit_text(f"Usage: <code>{prefix}specs<brand> <device></code>")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.devicespecifications.com/en/brand-more"
        ) as resp:
            content = await resp.read()
        all_brands = (
            BeautifulSoup(content, "lxml")
            .find("div", {"class": "brand-listing-container-news"})
            .findAll("a")
        )
        brand_page_url = None
        try:
            brand_page_url = [
                i["href"] for i in all_brands if brand == i.text.strip().lower()
            ][0]
        except IndexError:
            await message.edit_text(f"{brand} is unknown brand!")

        async with session.get(brand_page_url) as resp:
            content = await resp.read()
        devices = BeautifulSoup(content, "lxml").findAll(
            "div", {"class": "model-listing-container-80"}
        )
        device_page_url = None
        try:
            device_page_url = [
                i.a["href"]
                for i in BeautifulSoup(str(devices), "lxml").findAll("h3")
                if device in i.text.strip().lower()
            ]
        except IndexError:
            await message.edit_text(f"can't find {device}!")
        if len(device_page_url) > 2:
            device_page_url = device_page_url[:2]
        reply = ""
        for url in device_page_url:
            async with session.get(url) as resp:
                content = await resp.read()
            info = BeautifulSoup(content, "lxml")
            reply = "\n" + info.title.text.split("-")[0].strip() + "\n\n"
            info = info.find("div", {"id": "model-brief-specifications"})
            specifications = re.findall(r"<b>.*?<br/>", str(info))
            for item in specifications:
                title = re.findall(r"<b>(.*?)</b>", item)[0].strip()
                data = (
                    re.findall(r"</b>: (.*?)<br/>", item)[0]
                    .replace("<b>", "")
                    .replace("</b>", "")
                    .strip()
                )
                reply += f"{title}: {data}\n"
    await message.edit_text(reply)


modules_help["specs"] = {
    "specs": "Gets the specifications of a mobile device."
    + "\n\nUsage: `.specs <brand> <device>`"
    + "\n\nExample: `.specs samsung galaxy s20 ultra`"
}
