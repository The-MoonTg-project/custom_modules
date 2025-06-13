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


from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library
from utils.db import db

import_library("dub")

import dub


@Client.on_message(filters.command("dub", prefix) & filters.me)
async def dub_short(_, message: Message):
    if len(message.command) > 1:
        link = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        link = message.reply_to_message.text
    else:
        await message.edit(f"<b>Usage: </b><code>{prefix}short [url to short]</code>")
        return
    token = db.get("custom.dub", "key", None)
    if not token:
        await message.edit("<b>Dub API key not set!</b>")
        return
    try:
        dub_client = dub.Dub(token=token)
        request = {
            "url": link,
            "domain": "git.new" if "github.com" or "gitlab.com" in link else "dub.sh",
        }
        short_url = (await dub_client.links.upsert_async(request=request)).short_link
        await message.edit(
            f"<b>Shortened Url:</b> <code>{short_url}</code>",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await message.edit(f"<b>Error:</b> <code>{format_exc(e)}</code>")


@Client.on_message(filters.command("dubset", prefix) & filters.me)
async def dub_set(_, message: Message):
    if len(message.command) > 1:
        token = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        token = message.reply_to_message.text
    else:
        await message.edit(f"<b>Usage: </b><code>{prefix}dubset [api key]</code>")
        return
    db.set("custom.dub", "key", token)
    await message.edit("<b>Dub API key set!</b>")


@Client.on_message(filters.command("dubdel", prefix) & filters.me)
async def dub_del(_, message: Message):
    db.remove("custom.dub", "key")
    await message.edit("<b>Dub API key deleted!</b>")


modules_help["dub"] = {
    "dub [url|reply]*": "short url",
    "dubset [key|reply]*": "set dub api key",
    "dubdel": "delete dub api key",
}
