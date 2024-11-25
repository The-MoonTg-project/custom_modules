import asyncio
import os
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

# Media cache and processing tasks
user_media_cache = defaultdict(list)
media_processing_tasks = {}

# Helper to get group-specific data
def get_group_data(group_id):
    return db.get(f"custom.mlog", str(group_id), {})

# Helper to update group-specific data
def update_group_data(group_id, data):
    db.set(f"custom.mlog", str(group_id), data)


@Client.on_message(filters.command(["mlog"], prefix) & filters.me)
async def mlog(_, message: Message):
    if len(message.command) < 2 or message.command[1].lower() not in ["on", "off"]:
        return await message.edit(f"<b>Usage:</b> <code>{prefix}mlog [on/off]</code>")

    status = message.command[1].lower() == "on"
    db.set("custom.mlog", "status", status)
    await message.edit(f"<b>Media logging is now {'enabled' if status else 'disabled'}</b>")


@Client.on_message(filters.command(["msetchat"], prefix) & filters.me)
async def set_chat(_, message: Message):
    if len(message.command) < 2:
        return await message.edit(f"<b>Usage:</b> <code>{prefix}msetchat [chat_id]</code>")

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
    user_id = message.from_user.id
    user_media_cache[user_id].append(message)

    if user_id not in media_processing_tasks:
        media_processing_tasks[user_id] = asyncio.create_task(process_media(client, message.from_user))


async def process_media(client: Client, user):
    await asyncio.sleep(5)  # Wait to group incoming media
    user_id = user.id

    me = await client.get_me()
    if user_id == me.id:
        return

    chat_id = db.get("custom.mlog", "chat")
    if not chat_id:
        return await client.send_message(
            "me",
            f"Media Logger is on, but no Chat ID is set. Use {prefix}msetchat to set it.",
        )

    group_data = get_group_data(chat_id)
    user_topics = group_data.get("user_topics", {})
    topic_id = user_topics.get(str(user_id))  # Fetch user's topic ID if it exists

    if not topic_id:
        topic = await client.create_forum_topic(chat_id, user.first_name)
        topic_id = topic.id
        user_topics[str(user_id)] = topic_id  # Store topic ID for this user
        update_group_data(chat_id, {"user_topics": user_topics})
        m = await client.send_message(
            chat_id=chat_id,
            message_thread_id=topic_id,
            text=f"<b>Chat Name:</b> {user.full_name}\n<b>User ID:</b> {user_id}\n<b>Username:</b> @{user.username or 'N/A'}\n<b>Phone No:</b> +{user.phone_number or 'N/A'}",
        )
        await m.pin()

    messages_to_process = user_media_cache.pop(user_id, [])
    for media_message in messages_to_process:
        try:
            await media_message.copy(chat_id=chat_id, message_thread_id=topic_id)
            await asyncio.sleep(1)  # Delay between sending media
        except (FileReferenceExpired, FileReferenceInvalid):
            # Handle self-destruct photos and video notes
            await handle_self_destruct_media(client, media_message, chat_id, topic_id)
        except TopicDeleted:
            topic = await client.create_forum_topic(chat_id, user.first_name)
            topic_id = topic.id
            user_topics[str(user_id)] = topic_id  # Update the new topic ID
            update_group_data(chat_id, {"user_topics": user_topics})
            await client.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                text=f"<b>Chat Name:</b> {user.full_name}\n<b>User ID:</b> {user_id}\n<b>Username:</b> @{user.username or 'N/A'}\n<b>Phone No:</b> +{user.phone_number or 'N/A'}",
            )
            await handle_self_destruct_media(client, media_message, chat_id, topic_id)
        except TopicClosed:
            await client.reopen_forum_topic(chat_id=chat_id, topic_id=topic_id)
            await media_message.copy(chat_id=chat_id, message_thread_id=topic_id)

    media_processing_tasks.pop(user_id, None)


async def handle_self_destruct_media(client: Client, message: Message, chat_id: int, topic_id: int):
    try:
        # Download the self-destructing media
        file_path = await message.download()
        if message.photo:
            await client.send_photo(chat_id, file_path, message_thread_id=topic_id)
        elif message.video_note:
            await client.send_video(chat_id, file_path, message_thread_id=topic_id)
        os.remove(file_path)  # Clean up after sending
    except Exception as e:
        print(f"Error handling self-destructing media: {e}")


modules_help["mlog"] = {
    "mlog [on/off]": "Enable or disable media logging",
    "msetchat [chat_id]": "Set the chat ID for media logging",
}
