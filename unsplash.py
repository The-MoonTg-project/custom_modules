# feel free to use this in any pyrogram library userbot plugin you'll face no errors
import asyncio
import aiohttp
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

# taken from pyrogram documentation if not works kindly inform me :)


class AioHttp:

    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()

    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()

    async def get_url(self, link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return resp.url


@Client.on_message(filters.command("unsplash", prefix) & filters.me)
async def unsplash(client: Client, message: Message):
    if len(message.command) > 1 and isinstance(message.command[1], str):
        keyword = message.command[1]

        if len(message.command) > 2 and int(message.command[2]) < 10:
            await message.edit("<b>Getting Pictures</b>")
            count = int(message.command[2])
            images = []
            while len(images) is not count:
                img = await AioHttp().get_url(
                    f"https://source.unsplash.com/1600x900/?{keyword}"
                )
                if img not in images:
                    images.append(img)

            for img in images:
                await client.send_photo(message.chat.id, str(img))

            await message.delete()
            return
        else:
            await message.edit("<b>Getting Picture</b>")
            img = await AioHttp().get_url(
                f"https://source.unsplash.com/1600x900/?{keyword}"
            )
            await asyncio.gather(
                message.delete(),
                client.send_photo(message.chat.id, str(img))
            )

modules_help["unsplash"] = {
    "unsplash": f"[keyword]*",
    "unsplash": f"[keyword]* [number of results you want]*"
}
