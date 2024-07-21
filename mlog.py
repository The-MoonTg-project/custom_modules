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
from pyrogram.errors import FileReferenceExpired, FileReferenceInvalid
from pyrogram.types import Message

from utils.db import db
from utils.misc import modules_help, prefix

mlog_enabled = filters.create(lambda _, __, ___: db.get("custom.mlog", "status", False))


@Client.on_message(filters.command(["mlog"], prefix) & filters.me)
async def mlog(_, message: Message):
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}mlog [on/off]</code>")
        return
    if message.command[1].lower() == "on":
        db.set("custom.mlog", "status", True)
        return await message.edit("<b>Media logging is now enabled</b>")
    elif message.command[1].lower() == "off":
        db.set("custom.mlog", "status", False)
        return await message.edit("<b>Media logging is now disabled</b>")
    return await message.edit(f"<b>Usage:</b> <code>{prefix}mlog [on/off]</code>")


@Client.on_message(filters.command(["msetchat"], prefix) & filters.me)
async def set_chat(_, message: Message):
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}msetchat [chat_id]</code>")
        return
    try:
        chat_id = message.command[1]
        if not chat_id.startswith("-100"):
            chat_id = "-100" + str(chat_id)
        chat_id = int(chat_id)
        db.set("custom.mlog", "chat", chat_id)
        await message.edit(f"<b>Chat ID set to {chat_id}</b>")
    except ValueError:
        await message.edit("<b>Invalid chat ID</b>")


@Client.on_message(
    filters.media
    & filters.incoming
    & ~filters.channel
    & ~filters.group
    & ~filters.bot
    & mlog_enabled
)
async def media_log(client: Client, message: Message):
    chat_id = db.get("custom.mlog", "chat")
    chat_name = message.chat.full_name
    user_id = message.chat.id
    user_name = message.chat.username
    user = await client.get_users(user_id)
    user_num = user.phone_number
    if chat_id is None:
        await client.send_message(
            "me",
            f"Your Media Logger is on however you haven't set any Chat ID. Use {prefix}msetchat to set it.",
        )
        return
    topics = {}
    async for topic in client.get_forum_topics(chat_id):
        # Save topic id and title into topics dict
        topics[topic.id] = topic.title
        # Check if chat_name is present in topics
    if chat_name in topics.values():
        # Get the corresponding id for chat_name
        topic_id = [k for k, v in topics.items() if v == chat_name][0]
        try:
            await message.copy(chat_id=chat_id, message_thread_id=topic_id)
        except (FileReferenceExpired, FileReferenceInvalid):
            pass
    else:
        # Create a topic with chat_name as title
        new_topic = await client.create_forum_topic(chat_id, chat_name)
        # Save the new topic id and title into topics dict
        topics[new_topic.id] = new_topic.title
        m = await client.send_message(
            chat_id=chat_id,
            message_thread_id=new_topic.id,
            text=f"Chat Name: {chat_name}\nUser ID: {user_id}\nUsername: {user_name}\nPhone num: {user_num}",
        )
        await m.pin()
        try:
            await message.copy(chat_id=chat_id, message_thread_id=new_topic.id)
        except (FileReferenceExpired, FileReferenceInvalid):
            pass


modules_help["mlog"] = {
    "mlog [on/off]": "Enable or disable media logging",
    "msetchat [chat_id]": "Set the chat where media logging should be done",
}
