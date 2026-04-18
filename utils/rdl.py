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
from utils.reaction_handler import PeerReaction
from utils.scripts import format_exc, progress


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
        return await message.edit_text("Please provide an emoji.")


@on_message_reactions_updated()
async def rdl(client: Client, update: MessageReactionsUpdated):
    tchat = db.get("custom.rdl", "chat_id", default="me")
    temoji = db.get("custom.rdl", "emoji", default="🌚")
    if not tchat or not update.recent_reactions:
        return
    reaction: PeerReaction = update.recent_reactions[0]
    if reaction.reaction.emoji == temoji:
        from_chat = update.chat.id
        selected_id = update.msg_id
        c_time = time.time()
        try:
            ms = await client.send_message(
                tchat, f"Working on message {selected_id}..."
            )
            selected_message = await client.get_messages(from_chat, selected_id)
            file_text = selected_message.caption

            try:
                # Try to download the media
                file = await client.download_media(
                    selected_message,
                    progress=progress,
                    progress_args=(ms, c_time, "<code>Trying to download...</code>"),
                )
                await client.send_document(
                    tchat,
                    file,
                    caption=file_text,
                    progress=progress,
                    progress_args=(ms, c_time, "<code>Uploading...</code>"),
                )
                os.remove(file)
            except ValueError:
                # If downloading is restricted, try to copy the message
                await client.copy_message(tchat, from_chat, selected_id)
            except ChatForwardsRestricted:
                pass
            await ms.delete()
        except Exception:
            pass


@Client.on_message(filters.command("rdl", prefix) & filters.me)
async def dl(client: Client, message: Message):
    # Extract command arguments
    args = message.command[1:]

    # Check if the required arguments are provided
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
        # Join the chat if not already a participant
        await client.join_chat(ch_gp_link)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        await message.edit_text(format_exc(e))
        return

    try:
        # Get the chat object
        chat = await client.get_chat(ch_gp_link)
        from_chat = chat.id

        # Download and re-upload the specified number of messages
        for _ in range(num_messages):
            ms = await message.edit_text(f"Working on message {selected_id}...")
            selected_message = await client.get_messages(from_chat, selected_id)
            file_text = selected_message.caption

            try:
                # Try to download the media
                file = await client.download_media(
                    selected_message,
                    progress=progress,
                    progress_args=(ms, c_time, "<code>Trying to download...</code>"),
                )
                await client.send_document(
                    chat_id,
                    file,
                    caption=file_text,
                    progress=progress,
                    progress_args=(ms, c_time, "<code>Uploading...</code>"),
                )
                os.remove(file)
            except ValueError:
                # If downloading is restricted, try to copy the message
                await client.copy_message(chat_id, from_chat, selected_id)
            except ChatForwardsRestricted:
                pass

            selected_id += 1

        await ms.delete()
    except Exception as e:
        await message.edit_text(format_exc(e))


modules_help["rdl"] = {
    "rdl channel_link message_id [number_of_messages]": "download restricted content. Note that number_of_messages is optional if you only want a single message to be downloaded, then don't provide it",
    "rdl_chat chat_id": "set the destination chat ID",
    "rdl_emoji emoji": "set the emoji used to trigger the download by reaction",
}
