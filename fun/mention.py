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
from pyrogram.types.user_and_chats.user import Link

from utils.misc import modules_help, prefix


def custom_mention(user, custom_text):
    return Link(
        f"tg://user?id={user.id}",
        custom_text,
        user._client.parse_mode,
    )


@Client.on_message(filters.command("mention", prefix) & filters.me)
async def example_edit(client: Client, message: Message):
    chat_id = message.chat.id
    if message.reply_to_message and not len(message.text.split()) > 1:
        user = message.reply_to_message.from_user
        custom_text = (
            message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        )
        if custom_text:
            await message.edit(custom_mention(user, custom_text))
        else:
            await message.delete()
            await client.send_message(chat_id, user.mention)
    else:
        if len(message.text.split()) > 1:
            user_id = message.text.split()[1]
            if user_id.isdigit():
                text = (
                    message.text.split(maxsplit=2)[2]
                    if len(message.text.split()) > 2
                    else None
                )
                if text:
                    men = Link(f"tg://user?id={user_id}", text, client.parse_mode)
                else:
                    men = (await client.get_users(user_id)).mention
                await message.edit(men)
            else:
                await message.edit("Invalid user_id")
                await message.delete()
        else:
            await message.edit("Reply to a message or provide a user_id")
            await message.delete()


modules_help["mention"] = {
    "mention": "Mention the user you replied to.",
    "mention [custom_text]": "Mention the user you replied to with custom text.",
    "mention [user_id] [custom_text]": "Mention a user by their user_id with custom text.",
    "mention [user_id]": "Mention a user by their user_id.",
}
