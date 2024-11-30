# This Module is a part of MoonUserbot and is used here for example
import time
import os

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant, ChatForwardsRestricted

from utils.misc import modules_help, prefix
from utils.scripts import progress, format_exc


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

    chat_id = message.chat.id
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
                    progress_args=(ms, c_time, f"`Trying to download...`"),
                )
                await client.send_document(
                    chat_id,
                    file,
                    caption=file_text,
                    progress=progress,
                    progress_args=(ms, c_time, f"`Uploading...`"),
                )
                os.remove(file)
            except ValueError:
                # If downloading is restricted, try to copy the message
                await client.copy_message(chat_id, from_chat, selected_id)
            except ChatForwardsRestricted:
                # If downloading is restricted, try to copy the message
                pass

            selected_id += 1

        await ms.delete()
    except Exception as e:
        await message.edit_text(format_exc(e))


modules_help["rdl"] = {
    "rdl channel_link message_id [number_of_messages]": "download restricted content. Note that number_of_messages is optional if you only want a single message to be downloaded, then don't provide it",
}
