from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChannelInvalid, PeerIdInvalid
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("anon", prefix) & filters.me)
async def anon(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit(
            "<b>Usage:</b> <code>anon [channel_id] [message]</code> or reply to a message to forward it.",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    try:
        source_chat_id = message.chat.id
        anon_channel_id = int(message.command[1])
        text_content = " ".join(message.command[2:]) if len(message.command) > 2 else None
    except (ValueError, IndexError):
        await message.edit(
            "<b>Error:</b> Invalid command format. Use <code>anon [channel_id] [text]</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    replied_to_message = message.reply_to_message

    if not replied_to_message and not text_content:
        await message.edit(
            "<b>Error:</b> You must provide text or reply to a message/media.",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    original_message_id = message.id

    try:
        await message.delete()

        if replied_to_message:
            sent_message = await replied_to_message.copy(anon_channel_id)
        else:
            sent_message = await client.send_message(
                chat_id=anon_channel_id,
                text=text_content,
                parse_mode=enums.ParseMode.MARKDOWN,
            )

        await sent_message.forward(source_chat_id)

    except (ChannelInvalid, PeerIdInvalid):
        await client.send_message(
            chat_id=source_chat_id,
            text=f"<b>Error:</b> The ID <code>{anon_channel_id}</code> is invalid or I am not an admin in that channel.",
            parse_mode=enums.ParseMode.HTML,
        )
    except FloodWait as e:
        await client.send_message(
            chat_id=source_chat_id,
            text=f"<b>FloodWait:</b> Please wait for {e.value} seconds.",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        await client.send_message(
            chat_id=source_chat_id,
            text=f"<b>An unexpected error occurred:</b>\n<code>{e}</code>",
            parse_mode=enums.ParseMode.HTML,
        )

modules_help["anonymizer"] = {
    "anon [id] [message]": "Sends a text message to the specified channel/group ID and then forwards it to the current chat, hiding the original sender. The original command is deleted.",
    "anon [id] (as reply)": "Copies the replied-to message/media to the specified channel/group ID and then forwards it to the current chat, hiding the original sender. The original command is deleted.",
}
