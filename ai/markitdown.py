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

import os
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help
from utils.scripts import prefix, import_library, with_reply

import_library("markitdown")

from markitdown import MarkItDown


@Client.on_message(filters.command(["markitdown", "mkdn"], prefix) & filters.me)
@with_reply
async def markitdown(client: Client, message: Message):
    if message.reply_to_message.document:
        await message.edit("Converting to Markdown...")
        file = await message.reply_to_message.download()
        file_name = (message.reply_to_message.document.file_name).split(".")[0] + ".md"
        markitdown = MarkItDown()
        result = markitdown.convert(file)
        with open(file_name, "w") as f:
            f.write(result.text_content)
        await message.edit("Uploading...")
        await client.send_document(
            message.chat.id, file_name, reply_to_message_id=message.reply_to_message.id
        )
        os.remove(file)
        os.remove(file_name)
        await message.delete()
    else:
        await message.edit("Reply to a document to convert it to Markdown.")


modules_help["markitdown"] = {"markitdown": "Convert a document to Markdown."}
