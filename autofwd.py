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
from pyrogram.errors import MessageTooLong

from utils.misc import modules_help, prefix
from utils.db import db


def addtrg(channel_id):
    channel_ids = db.get("custom.autofwd", "chatto", default=[])
    if channel_id not in channel_ids:
        channel_ids.append(channel_id)
        db.set("custom.autofwd", "chatto", channel_ids)


def rmtrg(channel_id):
    channel_ids = db.get("custom.autofwd", "chatto", default=[])
    if channel_id in channel_ids:
        channel_ids.remove(channel_id)
        db.set("custom.autofwd", "chatto", channel_ids)


def addsrc(channel_id):
    channel_ids = db.get("custom.autofwd", "chatsrc", default=[])
    if channel_id not in channel_ids:
        channel_ids.append(channel_id)
        db.set("custom.autofwd", "chatsrc", channel_ids)


def rmsrc(channel_id):
    channel_ids = db.get("custom.autofwd", "chatsrc", default=[])
    if channel_id in channel_ids:
        channel_ids.remove(channel_id)
        db.set("custom.autofwd", "chatsrc", channel_ids)


def getfwd_data():
    source_chats = db.get("custom.autofwd", "chatsrc")
    target_chats = db.get("custom.autofwd", "chatto")
    return source_chats, target_chats


@Client.on_message(filters.command(["addfwd_src", "addfwd_to"], prefix) & filters.me)
async def addfwd(_, message: Message):
    if message.command[0] == "addfwd_src":
        if len(message.command) > 1:
            channel_id = message.text.split(maxsplit=1)[1]
            if not channel_id.startswith("-100"):
                channel_id = "-100" + channel_id
            # chat id should be integer
            if not channel_id.isdigit():
                try:
                    channel_id = int(channel_id)
                except Exception:
                    return await message.edit_text("Chat id should be in integer")
            addsrc(channel_id=channel_id)
            await message.edit_text(
                f"Auto Forwarding Enabled for Chat with id: <code>{channel_id}</code>"
            )
        else:
            await message.edit_text("Chat id not provided!")
            return
    elif message.command[0] == "addfwd_to":
        if len(message.command) > 1:
            channel_id = message.text.split(maxsplit=1)[1]
            if not channel_id.startswith("-100"):
                channel_id = "-100" + channel_id
            # chat id should be integer
            if not channel_id.isdigit():
                try:
                    channel_id = int(channel_id)
                except Exception:
                    return await message.edit_text("Chat id should be in integer")
            addtrg(channel_id=channel_id)
            await message.edit_text(
                f"Auto Forwarding Enabled to Chat with id: <code>{channel_id}</code>"
            )
        else:
            await message.edit_text("Chat id not provided!")
            return


@Client.on_message(filters.command(["delfwd_src", "delfwd_to"], prefix) & filters.me)
async def delfwd(_, message: Message):
    if message.command[0] == "delfwd_src":
        if len(message.command) > 1:
            channel_id = message.text.split(maxsplit=1)[1]
            if not channel_id.startswith("-100"):
                channel_id = "-100" + channel_id
            # chat id should be integer
            if not channel_id.isdigit():
                try:
                    channel_id = int(channel_id)
                except Exception:
                    return await message.edit_text("Chat id should be in integer")
            rmsrc(channel_id=channel_id)
            await message.edit_text(
                f"Auto Forwarding Disabled for Chat with id: <code>{channel_id}</code>"
            )
        else:
            await message.edit_text("Chat id not provided!")
            return
    elif message.command[0] == "delfwd_to":
        if len(message.command) > 1:
            channel_id = message.text.split(maxsplit=1)[1]
            if not channel_id.startswith("-100"):
                channel_id = "-100" + channel_id
            # chat id should be integer
            if not channel_id.isdigit():
                try:
                    channel_id = int(channel_id)
                except Exception:
                    return await message.edit_text("Chat id should be in integer")
            rmtrg(channel_id=channel_id)
            await message.edit_text(
                f"Auto Forwarding Disabled to Chat with id: <code>{channel_id}</code>"
            )
        else:
            await message.edit_text("Chat id not provided!")
            return


@Client.on_message(filters.command("autofwd", prefix) & filters.me)
async def autofwd(_, message: Message):
    source_chats, target_chats = getfwd_data()
    return await message.edit_text(f"Source Chats: {source_chats}\nTarget Chats: {target_chats}")


@Client.on_message(filters.text & filters.channel)
async def autofwd_main(client: Client, message: Message):
    chat_id = message.chat.id
    source_chats = db.get("custom.autofwd", "chatsrc")
    target_chats = db.get("custom.autofwd", "chatto")

    if source_chats is not None and chat_id in source_chats:
        if target_chats is not None:
            for chat in target_chats:
                try:
                    await message.copy(chat, chat_id)
                except Exception as e:
                    try:
                        await client.send_message(
                            "me",
                            f"Auto Forwarding Failed for Chat with id: <code>{chat_id}</code> to <code>{chat}</code>\n\n{e}",
                        )
                    except MessageTooLong:
                        await client.send_message(
                            "me",
                            f"Auto Forwarding Failed for Chat with id: <code>{chat_id}</code> to <code>{chat}</code>, Please check logs!",
                        )


modules_help["autofwd"] = {
    "autofwd": "Retrieve Data of auto fwd",
    "addfwd_src [channel_id]*": "Enable auto forwarding for a channel",
    "addfwd_to [channel_id]*": "Enable auto forwarding to a channel",
    "delfwd_src [channel_id]*": "Disable auto forwarding for a channel",
    "delfwd_to [channel_id]*": "Disable auto forwarding to a channel",
}
