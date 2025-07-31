import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid, ChannelInvalid
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("linksend", prefix) & filters.me)
async def linksend(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.edit("<b>You must reply to a media message.</b>")
        await asyncio.sleep(3)
        await message.delete()
        return

    if len(message.command) < 2:
        await message.edit(
            "<b>Usage:</b> <code>linksend [destination_chat_id] [optional_text]</code>"
        )
        await asyncio.sleep(3)
        await message.delete()
        return

    try:
        destination_chat_id = int(message.command[1])
    except ValueError:
        await message.edit("<b>The destination chat ID must be a valid number.</b>")
        await asyncio.sleep(3)
        await message.delete()
        return

    text = " ".join(message.command[2:]) if len(message.command) > 2 else ""
    replied_message = message.reply_to_message

    try:
        # Create the hyperlink message
        zwnj_char = "\u200d"  # Zero-width non-joiner character '‍'
        hyperlink = f"[{zwnj_char}]({replied_message.link})"
        
        text_to_send = f"{hyperlink} {text}" if text else hyperlink

        # Send the message to the destination
        await client.send_message(
            chat_id=destination_chat_id,
            text=text_to_send,
            disable_web_page_preview=False,
            parse_mode=enums.ParseMode.MARKDOWN,
        )

        # Remove the caption from the original media
        if replied_message.caption:
            await replied_message.edit_caption(caption=None)

        # Delete the command message
        await message.delete()

    except (PeerIdInvalid, ChannelInvalid):
        await message.edit(
            f"<b>Error:</b> Invalid destination chat ID (<code>{destination_chat_id}</code>). "
            "Make sure it's correct and I am a member of that chat."
        )
    except Exception as e:
        await message.edit(f"<b>An unexpected error occurred:</b>\n<code>{e}</code>")


modules_help["linksend"] = {
    "linksend [id] [text]*": "Must be a reply to a media. Removes the original caption and sends a hyperlink of the media to the target chat ID. Optional text will be added after the link."
}
