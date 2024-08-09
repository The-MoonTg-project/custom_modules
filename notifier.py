import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto


from utils.db import db
from utils.misc import modules_help, prefix


def set_or_get_previous_profile(chat_id):
    if not os.path.exists(f"previous_profiles/{chat_id}"):
        os.makedirs(f"previous_profiles/{chat_id}")
    if os.path.exists(f"previous_profiles/{chat_id}/profile.json"):
        with open(f"previous_profiles/{chat_id}/profile.json", "r") as f:
            return json.load(f)
    else:
        return {}


@Client.on_message(filters.command("setlogchatid", prefix) & filters.me)
async def set_log_group_chat_id_command(client: Client, message: Message):
    try:
        if "-100" in message.command[1]:
            chat_id = int(message.command[1])
        else:
            chat_id = int(f"-100{message.command[1]}")
        set_log_group_chat_id(chat_id)
        await message.edit(f"Log group chat ID set to {chat_id}.")
    except (IndexError, ValueError):
        await message.edit("Please provide a valid chat ID.")


def set_log_group_chat_id(chat_id):
    db.set("custom.friendNotify", "logID", chat_id)


def update_previous_profile(chat_id, current_info):
    if not os.path.exists(f"previous_profiles/{chat_id}"):
        os.makedirs(f"previous_profiles/{chat_id}")
    with open(f"previous_profiles/{chat_id}/profile.json", "w") as f:
        json.dump(current_info, f)


@Client.on_message(filters.private & ~filters.chat("me") & ~filters.bot)
async def track_profile_changes(client: Client, message: Message):
    LOG_GROUP_CHAT_ID = db.get("custom.friendNotify", "logID", None)
    if LOG_GROUP_CHAT_ID is None:
        await client.send_message(
            "me",
            f"Log group chat ID is not set for notifier. Please set it using <code>{prefix}setlogchatid <chat_id></code>",
        )
        return
    chat_id = str(message.chat.id)
    previous_info = set_or_get_previous_profile(chat_id)
    user_chat = await client.get_chat(chat_id)
    current_info = {
        "username": user_chat.username,
        "first_name": user_chat.first_name,
        "last_name": user_chat.last_name,
        "bio": user_chat.bio,
        "photo": user_chat.photo.big_file_id if user_chat.photo else None,
    }

    changes = []

    if previous_info.get("username") != current_info.get("username"):
        changes.append(
            f"Previous Username: @{previous_info.get('username')}\nNew Username: @{current_info.get('username')}"
        )
    if previous_info.get("first_name") != current_info.get("first_name"):
        changes.append(
            f"Previous First Name: {previous_info.get('first_name')}\nNew First Name: {current_info.get('first_name')}"
        )
    if previous_info.get("last_name") != current_info.get("last_name"):
        changes.append(
            f"Previous Last Name: {previous_info.get('last_name')}\nNew Last Name: {current_info.get('last_name')}"
        )
    if previous_info.get("bio") != current_info.get("bio"):
        changes.append(
            f"Previous Bio: {previous_info.get('bio') if previous_info.get('bio') else 'Not available'}\nNew Bio: {current_info.get('bio') if current_info.get('bio') else 'Not available'}"
        )
    if previous_info.get("photo") != current_info.get("photo"):
        if os.path.exists(f"previous_profiles/{chat_id}/current.jpg"):
            os.rename(
                f"previous_profiles/{chat_id}/current.jpg",
                f"previous_profiles/{chat_id}/previous.jpg",
            )

            await client.download_media(
                current_info.get("photo"),
                file_name=f"previous_profiles/{chat_id}/current.jpg",
            )
        else:

            await client.download_media(
                current_info.get("photo"),
                file_name=f"previous_profiles/{chat_id}/current.jpg",
            )
        changes.append(
            f"Previous Profile Picture: {previous_info.get('photo')}\nNew Profile Picture: {current_info.get('photo')}"
        )

    if changes:
        if "Profile Picture" in changes[0]:

            change_msg = f"<b>Profile changes detected</b>\nFirst Name: {message.chat.first_name}\nLast Name: {message.chat.last_name}\nID: <code>{chat_id}</code>\nUsername: @{message.chat.username}"
            await client.send_message(LOG_GROUP_CHAT_ID, change_msg)
            if not os.path.exists(f"previous_profiles/{chat_id}/previous.jpg"):
                await client.send_photo(
                    LOG_GROUP_CHAT_ID,
                    f"previous_profiles/{chat_id}/current.jpg",
                    caption="New Profile",
                )
            await client.send_media_group(
                LOG_GROUP_CHAT_ID,
                media=[
                    InputMediaPhoto(
                        f"previous_profiles/{chat_id}/current.jpg",
                        caption="New Profile",
                    ),
                    InputMediaPhoto(
                        f"previous_profiles/{chat_id}/previous.jpg",
                        caption="Previous Profile",
                    ),
                ],
            )
        else:
            change_msg = (
                f"<b>Profile changes detected</b>\nFirst Name: {message.chat.first_name}\nLast Name: {message.chat.last_name}\nID: <code>{chat_id}</code>\nUsername: @{message.chat.username}\n\nChanges:\n"
                + "\n".join(changes)
            )
            await client.send_message(LOG_GROUP_CHAT_ID, change_msg)

    update_previous_profile(chat_id, current_info)


modules_help["notifier"] = {
    "notifier": "Notifies in the log group if a friend's profile picture, username, name, or bio changes.",
    "setlogchatid [chat_id]*": "Sets the log group chat ID for notifier.",
}
