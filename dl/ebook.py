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

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix


from utils.scripts import import_library

libgen_api = import_library("libgen_api", "libgen-api")
from libgen_api import LibgenSearch


@Client.on_message(filters.command("ebook", prefix) & filters.me)
async def ebook_search(_, message: Message):
    if len(message.command) < 2:
        return await message.edit("Give me something to search for!")
    text = message.text.split(maxsplit=1)[1]
    m = await message.edit("Searching...")
    s = LibgenSearch()
    results = s.search_title_filtered(
        text,
        {
            "Extension": "epub",
            "Language": "English",
        },
    )
    await m.edit(
        f"<b>Search Query:</b>\n<code>{text}</code>\n\n<b>Results:</b>\n{''.join([f'<a href="{i['Mirror_1']}">{i['Title']}</a>\n\n' for i in results])}",
        disable_web_page_preview=True,
    )


modules_help["ebook"] = {
    "ebook": "Search for ebooks on libgen.rs"
    f"\n<b>Example:</b> <code>{prefix}ebook Pride and Prejudice</code>",
}
