import os
from random import randint

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix


async def download_sticker(url, filename):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9;q=0.8",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    }
    cookies = {"country": "US", "lang": "en"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, cookies=cookies) as response:
            if response.status == 200:
                with open(filename, "wb") as f:
                    f.write(await response.read())


@Client.on_message(filters.command(["f"], prefix) & filters.me)
async def random_stiker(client: Client, message: Message):
    await message.delete()
    random = randint(1, 63)
    index = f"00{random}" if random < 10 else f"0{random}"
    sticker = (
        f"https://www.chpic.su/_data/stickers/f/FforRespect/FforRespect_{index}.webp"
    )
    await download_sticker(sticker, "f.webp")
    if os.path.exists("f.webp"):
        await client.send_document(
            message.chat.id,
            "f.webp",
            reply_to_message_id=message.reply_to_message.id
            if message.reply_to_message
            else None,
        )
        os.remove("f.webp")


modules_help["f"] = {"f": "Send f to pay respect"}
