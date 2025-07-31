import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, ReplyToInvalid
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("linksend", prefix) & filters.me)
async def linksend(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.edit("<b>You must reply to a media message.</b>", parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(3)
        await message.delete()
        return

    if len(message.command) < 2:
        await message.edit(
            "<b>Usage:</b> <code>linksend [destination_chat_id] [optional_text]</code>",
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(3)
        await message.delete()
        return

    try:
        destination_chat_id = int(message.command[1])
    except ValueError:
        await message.edit("<b>The destination chat ID must be a valid number.</b>", parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(3)
        await message.delete()
        return

    text = " ".join(message.command[2:]) if len(message.command) > 2 else ""
    replied_message = message.reply_to_message

    try:
        zwnj_char = "\u200d"
        hyperlink = f'<a href="{replied_message.link}">{zwnj_char}</a>'
        
        text_to_send = f"{hyperlink} {text}" if text else hyperlink

        await client.send_message(
            chat_id=destination_chat_id,
            text=text_to_send,
            disable_web_page_preview=False,
            parse_mode=enums.ParseMode.HTML,
        )

        if replied_message.caption:
            await replied_message.edit_caption(caption=None)

        await message.delete()

    except (PeerIdInvalid, ChannelInvalid):
        await message.edit(
            f"<b>Error:</b> Invalid destination chat ID (<code>{destination_chat_id}</code>). "
            "Make sure it's correct and I am in that chat.",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.edit(f"<b>An unexpected error occurred:</b>\n<code>{e}</code>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("rlinksend", prefix) & filters.me)
async def rlinksend(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.edit("<b>You must reply to a media message.</b>", parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(3)
        await message.delete()
        return

    if len(message.command) < 3:
        await message.edit(
            "<b>Usage:</b> <code>rlinksend [dest_id] [reply_to_msg_id] [text]</code>",
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(3)
        await message.delete()
        return

    try:
        destination_chat_id = int(message.command[1])
        reply_to_id = int(message.command[2])
    except ValueError:
        await message.edit("<b>Chat ID and Message ID must be valid numbers.</b>", parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(3)
        await message.delete()
        return

    text = " ".join(message.command[3:]) if len(message.command) > 3 else ""
    replied_message = message.reply_to_message

    try:
        zwnj_char = "\u200d"
        hyperlink = f'<a href="{replied_message.link}">{zwnj_char}</a>'
        
        text_to_send = f"{hyperlink} {text}" if text else hyperlink

        await client.send_message(
            chat_id=destination_chat_id,
            text=text_to_send,
            reply_to_message_id=reply_to_id,
            disable_web_page_preview=False,
            parse_mode=enums.ParseMode.HTML,
        )

        if replied_message.caption:
            await replied_message.edit_caption(caption=None)

        await message.delete()

    except (PeerIdInvalid, ChannelInvalid):
        await message.edit(
            f"<b>Error:</b> Invalid destination chat ID (<code>{destination_chat_id}</code>).",
            parse_mode=enums.ParseMode.HTML
        )
    except ReplyToInvalid:
        await message.edit(
            f"<b>Error:</b> Invalid <code>reply_to_message_id</code> in the destination chat.",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.edit(f"<b>An unexpected error occurred:</b>\n<code>{e}</code>", parse_mode=enums.ParseMode.HTML)


modules_help["linksend"] = {
    "linksend [id] [text]*": "Reply to media. Sends a hyperlink of it to the target chat ID. Removes original caption.",
    "rlinksend [id] [msg_id] [text]*": "Same as linksend, but replies to a specific message ID in the destination chat."
}
