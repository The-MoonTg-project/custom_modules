# This Module is a part of MoonUserbot and is used here for example
import os
import time

from pyrogram import Client, filters
from pyrogram.errors import ChatForwardsRestricted, UserAlreadyParticipant
from pyrogram.types import Message

from utils import (
    MessageReactionsUpdated,
    modules_help,
    on_message_reactions_updated,
    prefix,
)
from utils.db import db
from utils.scripts import format_exc, progress


async def _download_and_send(
    client: Client, tchat, from_chat: int, msg_id: int, status_msg=None, c_time: float = None
):
    if c_time is None:
        c_time = time.time()
    try:
        selected_message = await client.get_messages(from_chat, msg_id)
        if not selected_message:
            return
        file_text = selected_message.caption
        try:
            file = await client.download_media(
                selected_message,
                progress=progress,
                progress_args=(status_msg, c_time, "<code>Trying to download...</code>"),
            )
            await client.send_document(
                tchat,
                file,
                caption=file_text,
                progress=progress,
                progress_args=(status_msg, c_time, "<code>Uploading...</code>"),
            )
            os.remove(file)
        except ValueError:
            await client.copy_message(tchat, from_chat, msg_id)
        except ChatForwardsRestricted:
            pass
    except Exception:
        pass


def _check_chosen_order(reactions, temoji: str) -> bool:
    if not reactions:
        return False
    for r in reactions:
        if r.chosen_order is not None and r.emoji == temoji:
            return True
    return False


@Client.on_message(filters.command("rdl_chat", prefix) & filters.me)
async def rdl_chat(client: Client, message: Message):
    if len(message.command) > 1:
        dchat = db.get("custom.rdl", "chat_id", default="me")
        chat_id = message.text.split(maxsplit=1)[1]
        try:
            await client.get_chat(chat_id)
        except Exception:
            return await message.edit_text(
                "Chat ID is invalid or user is not a participant."
            )
        if dchat == chat_id:
            return await message.edit_text("This chat is already in the database.")
        else:
            db.set("custom.rdl", "chat_id", chat_id)
            return await message.edit_text(f"Chat ID: {chat_id} set.")
    else:
        return await message.edit_text("Please provide a chat ID.")


@Client.on_message(filters.command("rdl_emoji", prefix) & filters.me)
async def rdl_emoji(client: Client, message: Message):
    if len(message.command) > 1:
        temoji = message.text.split(maxsplit=1)[1]
        db.set("custom.rdl", "emoji", temoji)
        return await message.edit_text(f"Emoji: {temoji} set.")
    else:
        db.remove("custom.rdl", "emoji")
        return await message.edit_text("Emoji: 🌚 set.")


@on_message_reactions_updated()
async def rdl_reactions(client: Client, update: MessageReactionsUpdated):
    temoji = db.get("custom.rdl", "emoji", default="🌚")
    if not _check_chosen_order(update.reactions, temoji):
        return
    tchat = db.get("custom.rdl", "chat_id", default="me")
    if not tchat:
        return
    c_time = time.time()
    ms = await client.send_message(tchat, f"Working on message {update.msg_id}...")
    await _download_and_send(client, tchat, update.chat.id, update.msg_id, ms, c_time)
    await ms.delete()


@Client.on_message(filters.command("rdl", prefix) & filters.me)
async def dl(client: Client, message: Message):
    args = message.command[1:]

    if len(args) < 2:
        await message.edit_text(
            "Kindly use `.rdl channel_link message_id [number_of_messages]`"
        )
        return

    chat_id = db.get("custom.rdl", "chat_id", default=message.chat.id)
    c_time = time.time()
    ch_gp_link = args[0]
    selected_id = int(args[1])
    num_messages = int(args[2]) if len(args) > 2 else 1

    try:
        await client.join_chat(ch_gp_link)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        await message.edit_text(format_exc(e))
        return

    try:
        chat = await client.get_chat(ch_gp_link)
        from_chat = chat.id

        for _ in range(num_messages):
            ms = await message.edit_text(f"Working on message {selected_id}...")
            await _download_and_send(client, chat_id, from_chat, selected_id, ms, c_time)
            selected_id += 1

        await ms.delete()
    except Exception as e:
        await message.edit_text(format_exc(e))


modules_help["rdl"] = {
    "rdl channel_link message_id [number_of_messages]": "download restricted content. Note that number_of_messages is optional if you only want a single message to be downloaded, then don't provide it",
    "rdl_chat chat_id": "set the destination chat ID",
    "rdl_emoji emoji": "set the emoji used to trigger the download by reaction",
}
