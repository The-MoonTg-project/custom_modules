#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

URL = "https://deliriusapi-official.vercel.app/ia"


def clean_data(data):
    parts = data.split("$@$")

    if len(parts) > 1:
        return parts[-1]
    else:
        return data


@Client.on_message(filters.command(["wgpt", "gptweb"], prefix) & filters.me)
async def gptweb(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `wgpt <query>`")
        return
    await message.edit("Thinking...")
    query = " ".join(message.command[1:])
    url = f"{URL}/gptweb?text={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        await message.edit(
            f"**Question:**\n{query}\n**Answer:**\n{data['gpt']}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["bbox", "blackbox"], prefix) & filters.me)
async def blackbox(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `bbox <query>`")
        return
    await message.edit("Thinking...")
    query = " ".join(message.command[1:])
    url = f"{URL}/blackbox?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        data = data["data"]
        data = clean_data(data)
        await message.edit(
            f"**Question:**\n{query}\n**Answer:**\n{data}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command(["wgemini"], prefix) & filters.me)
async def gemini(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `wgemini <query>`")
        return
    await message.edit("Thinking...")
    query = " ".join(message.command[1:])
    url = f"{URL}/gemini?query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        await message.edit(
            f"**Question:**\n{query}\n**Answer:**\n{data['message']}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.edit("An error occurred, please try again later.")


modules_help["sarethai"] = {
    "wgpt [query]*": "Ask anything to GPT-Web",
    "bbox [query]*": "Ask anything to Blackbox",
    "gptweb [query]*": "Ask anything to GPT-Web",
    "blackbox [query]*": "Ask anything to Blackbox",
    "wgemini [query]*": "Ask anything to Gemini",
}
