#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix


async def get_neko(type):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://nekos.life/api/v2/img/{type}") as resp:
                data = await resp.json()
        return data.get("url", None)
    except Exception:
        return None


async def get_types():
    types = [
        "smug",
        "woof",
        "gasm",
        "8ball",
        "goose",
        "cuddle",
        "avatar",
        "slap",
        "pat",
        "gecg",
        "feed",
        "fox_girl",
        "lizard",
        "neko",
        "hug",
        "meow",
        "kiss",
        "wallpaper",
        "tickle",
        "spank",
        "waifu",
        "lewd",
        "ngif",
    ]
    return types


@Client.on_message(filters.command("ntype", prefix) & filters.me)
async def neko_types(_, message: Message):
    types = await get_types()
    await message.edit_text(
        "<b>Available Types:</b>\n<code>" + "</code>, <code>".join(types) + "</code>"
    )


@Client.on_message(filters.command("neko", prefix) & filters.me)
async def neko(client: Client, message: Message):
    if len(message.command) > 1:
        type = message.command[1]
    else:
        type = "neko"
    url = await get_neko(type)
    if url is None:
        await message.edit_text("Failed to fetch media.")
        return
    await message.delete()
    if ".gif" in url:
        await client.send_animation(message.chat.id, url)
    elif ".mp4" in url:
        await client.send_video(message.chat.id, url)
    else:
        await client.send_photo(message.chat.id, url)


@Client.on_message(filters.command("nspam", prefix) & filters.me)
async def neko_spam(client: Client, message: Message):
    if len(message.command) > 2:
        type = message.command[1]
        count = int(message.command[2])
    else:
        type = "neko"
        count = 10
    await message.delete()
    for _ in range(count):
        url = await get_neko(type)
        if url is None:
            continue
        if ".gif" in url:
            await client.send_animation(message.chat.id, url)
        elif ".mp4" in url:
            await client.send_video(message.chat.id, url)
        else:
            await client.send_photo(message.chat.id, url)


modules_help["neko"] = {
    "neko [type]": "Get a neko media (default: neko)",
    "ntype": "List available neko types",
    "nspam [type] [count]": "Spam neko media",
}
