import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import (
    FileReferenceExpired,
    FileReferenceInvalid,
    TopicDeleted,
    TopicClosed,
)
from pyrogram.types import Message
from collections import defaultdict

from utils.db import db
from utils.misc import modules_help, prefix

mlog_enabled = filters.create(lambda _, __, ___: db.get("custom.mlog", "status", False))

# Dictionary to store media messages per user temporarily
user_media_cache = defaultdict(list)


@Client.on_message(filters.command(["mlog"], prefix) & filters.me)
async def mlog(_, message: Message):
    if len(message.command) < 2 or message.command[1].lower() not in ["on", "off"]:
        return await message.edit(f"<b>Usage:</b> <code>{prefix}mlog [on/off]</code>")

    status = message.command[1].lower() == "on"
    db.set("custom.mlog", "status", status)
    await message.edit(
        f"<b>Media logging is now {'enabled' if status else 'disabled'}</b>"
    )


@Client.on_message(filters.command(["msetchat"], prefix) & filters.me)
async def set_chat(_, message: Message):
    if len(message.command) < 2:
        return await message.edit(
            f"<b>Usage:</b> <code>{prefix}msetchat [chat_id]</code>"
        )

    try:
        chat_id = message.command[1]
        chat_id = int("-100" + chat_id if not chat_id.startswith("-100") else chat_id)
        db.set("custom.mlog", "chat", chat_id)
        await message.edit(f"<b>Chat ID set to {chat_id}</b>")
    except ValueError:
        await message.edit("<b>Invalid chat ID</b>")


@Client.on_message(
    mlog_enabled
    & filters.incoming
    & filters.private
    & filters.media
    & ~filters.me
    & ~filters.bot
)
async def media_log(client: Client, message: Message):

    me = await client.get_me()
    user_name = ("@" + message.from_user.username) if message.from_user.username else message.from_user.first_name
    chat_name = message.from_user.full_name
    user_num = message.from_user.phone_number
    MY_USER_ID = me.id

    # Prevent logging your own media messages
    if message.from_user.id == MY_USER_ID:
        return

    chat_id = db.get("custom.mlog", "chat")
    if not chat_id:
        return await client.send_message(
            "me",
            f"Media Logger is on, but no Chat ID is set. Use {prefix}msetchat to set it.",
        )

    user_id, first_name = message.from_user.id, message.from_user.first_name
    user_media_cache[user_id].append(message)

    await asyncio.sleep(2)  # Adjust the delay as necessary

    topic_id = db.get(f"custom.mlog.topics.{user_id}", "topic_id")

    if not topic_id:
        topic_id = await client.create_forum_topic(chat_id, first_name)
        topic_id = topic_id.id
        db.set(f"custom.mlog.topics.{user_id}", "topic_id", topic_id)
        m = await client.send_message(
            chat_id=chat_id,
            message_thread_id=topic_id,
            text=f"Chat Name: {chat_name}\nUser ID: {user_id}\nUsername: {user_name}\nPhone num: {user_num}",
        )
        await m.pin()

    if len(user_media_cache[user_id]) != 0:
        messages_to_process = user_media_cache.pop(user_id, [])
    else:
        return

    for media_message in messages_to_process:
        try:
            await media_message.copy(chat_id=chat_id, message_thread_id=topic_id)
        except (FileReferenceExpired, FileReferenceInvalid):
            pass
        except TopicDeleted:
            topic_id = await client.create_forum_topic(chat_id, first_name)
            topic_id = topic_id.id
            db.set(f"custom.mlog.topics.{user_id}", "topic_id", topic_id)
            m = await client.send_message(
            chat_id=chat_id,
            message_thread_id=topic_id,
            text=f"Chat Name: {chat_name}\nUser ID: {user_id}\nUsername: {user_name}\nPhone num: {user_num}",
        )
            await m.pin()
            await media_message.copy(chat_id=chat_id, message_thread_id=topic_id)
        except TopicClosed:
            await client.reopen_forum_topic(chat_id=chat_id, topic_id=topic_id)
            await media_message.copy(chat_id=chat_id, message_thread_id=topic_id)


modules_help["mlog"] = {
    "mlog [on/off]": "Enable or disable media logging",
    "msetchat [chat_id]": "Set the chat ID where media logging should be done",
}
