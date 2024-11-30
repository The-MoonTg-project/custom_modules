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
import time

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, progress


@Client.on_message(filters.command("rename", prefix) & filters.me)
async def example_edit(client: Client, message: Message):
    try:
        thumb = "downloads/thumb/thumb.jpg"
        if not os.path.exists(thumb):
            thumb = "thumb.jpg"
        if not os.path.isfile(thumb):
            thumb = None
        i = await message.edit("<code>Renaming...</code>")
        if len(message.command) > 1:
            r_fname = message.text.split(maxsplit=1)[1]
            t = time.time()
            o_f = await message.reply_to_message.download(
                progress=progress,
                progress_args=(i, t, "`Renaming...`"),
            )
            os.rename(o_f, r_fname)
            await i.edit_text("<code>Done, Uploading...</code>")
            await client.send_document(
                message.chat.id,
                r_fname,
                reply_to_message_id=message.id,
                thumb=thumb,
                caption=r_fname,
                progress=progress,
                progress_args=(i, t, "`Done, Uploading...`"),
            )
            await i.delete()
        else:
            await message.edit_text(
                "lOl, Atleast reply to file and give new name (with extension ofc) to rename to -_-"
            )
    except Exception as e:
        await message.edit(format_exc(e))
    finally:
        os.remove(r_fname)


modules_help["rename"] = {
    "rename [reply]*": "rename file/media to given name and upload",
}
