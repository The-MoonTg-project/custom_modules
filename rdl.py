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
    chat_id = message.chat.id
    c_time = time.time()
    if len(message.command) > 2:
        ms = await message.edit_text("Working on it...")
        ch_gp_link = message.text.split()[1]
        selected_id = int(message.text.split()[2])
        try:
            await client.join_chat(ch_gp_link)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            await message.edit_text(format_exc(e))
        try:
            ch = await client.get_chat(ch_gp_link)
            from_chat = ch.id
            # Check if a third command is provided
            if len(message.command) > 3:
                num_messages = int(message.text.split()[3])
                for i in range(num_messages):
                    selected_id += i # Increment the message ID for each iteration
                    selected_message = await client.get_messages(from_chat, selected_id)
                    file_text = selected_message.caption
                    file = await client.download_media(selected_message, progress=progress, progress_args=(ms, c_time, f'`Trying to download...`'))
                    await client.send_document(chat_id, file, caption=file_text, progress=progress, progress_args=(ms, c_time, f'`Uploading...`'))
                    os.remove(file)
            else:
                selected_message = await client.get_messages(from_chat, selected_id)
                file_text = selected_message.caption
                file = await client.download_media(selected_message, progress=progress, progress_args=(ms, c_time, f'`Trying to download...`'))
                await client.send_document(chat_id, file, caption=file_text, progress=progress, progress_args=(ms, c_time, f'`Uploading...`'))
                os.remove(file)
            # await ms.delete()
        except ChatForwardsRestricted:
            pass
        except ValueError:
            try:
                if len(message.command) > 3:
                    num_messages = int(message.text.split()[3])
                    for i in range(num_messages):
                        selected_id += i # Increment the message ID for each iteration
                        selected_message = await client.get_messages(from_chat, selected_id)
                        file_text = selected_message.caption
                        await client.copy_message(chat_id, from_chat, selected_id)
                        # await ms.delete()
                else:
                    await client.copy_message(chat_id, from_chat, selected_id)
                    # await m
            except ChatForwardsRestricted:
                pass
        except Exception as e:
            await message.edit_text(format_exc(e))
        await ms.delete()
    else:
        await message.edit_text("Kindly use `.dl channel_link message_id [number_of_messages]`")

modules_help["rdl"] = {
    "rdl channel_link message_id [number_of_messages]": "download restricted content. Note that number of messages is optional if you only want single message to be downloaded then don't provide it",
}
