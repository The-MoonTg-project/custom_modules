import asyncio
import json
import os
import shutil

import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.types import Message
import requests
from utils.misc import modules_help, prefix


class AioHttp:
    async def get_json(self, link):
        headers = {
            "accept": "*/*",
            "accept-language": "en-US",
            "cache-control": "no-cache",
            "client-geo-region": "global",
            "dnt": "1",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=headers) as resp:
                return await resp.json()


@Client.on_message(filters.command("unsplash", prefix) & filters.me)
async def unsplash(client: Client, message: Message):
    if len(message.command) > 1 and isinstance(message.command[1], str):
        keyword = message.command[1]
        unsplash_dir = "downloads/unsplash/"
        if not os.path.exists(unsplash_dir):
            os.makedirs(unsplash_dir)

        if len(message.command) > 2 and 2 <= int(message.command[2]) <= 10:
            await message.edit(
                "<b>Getting Pictures</b>", parse_mode=enums.ParseMode.HTML
            )
            count = int(message.command[2])
            images = []
            data = await AioHttp().get_json(
                f"https://unsplash.com/napi/search/photos?page=1&per_page={count}&query={keyword}"
            )
            while len(images) < count:
                for ia in range(len(images), count):
                    img = data["results"][ia]["urls"]["raw"]
                    if img.startswith("https://images.unsplash.com/photo"):
                        image_content = requests.get(img).content
                        with open(f"{unsplash_dir}/unsplash_{ia}.jpg", "wb") as f:
                            f.write(image_content)
                        imgr = f"{unsplash_dir}/unsplash_{ia}.jpg"
                        images.append(imgr)
                    else:
                        images.append(img)
                    if len(images) == count:
                        break

            for img in images:
                await client.send_document(message.chat.id, img)

            await message.delete()
            shutil.rmtree(unsplash_dir)
            return
        else:
            await message.edit(
                "<b>Getting Picture</b>", parse_mode=enums.ParseMode.HTML
            )
            data = await AioHttp().get_json(
                f"https://unsplash.com/napi/search/photos?page=1&per_page=1&query={keyword}"
            )
            img = data["results"][0]["urls"]["raw"]
            await asyncio.gather(
                message.delete(), client.send_document(message.chat.id, str(img))
            )


modules_help["unsplash"] = {
    "unsplash": f"[keyword]*",
    "unsplash": f"[keyword]* [number of results you want]*\n"
    "Makes a request to <code>unsplash.com</code> and sends the image with the keyword you provided.\n\n"
    "<b>Note:</b>\n1. The number of results you can get is limited to 10.\n"
    "2. Keyword is required and should be of one word only!.\n"
    "3. Images are sent as document to maintain quality.",
}
