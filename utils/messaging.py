from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatForwardsRestricted

from utils.misc import modules_help, prefix
from utils.scripts import with_reply


@Client.on_message(filters.command("dm", prefix) & filters.me)
@with_reply
async def example_edit(client: Client, message: Message):
    reply_msg = message.reply_to_message.id
    if len(message.command) > 1:
        chat_id = message.text.split(maxsplit=1)[1]
        try:
            await client.copy_message(
                chat_id=chat_id, from_chat_id=message.chat.id, message_id=reply_msg
            )
        except ChatForwardsRestricted:
            await message.edit(
                "<code>Current chat has restricted message copy/forwards.</code>"
            )
            return
        await message.edit("<code>Message sent</code>")
        await message.delete()
    else:
        await message.edit("<code>Target not specified</code>")


@Client.on_message(filters.command(["schedule", "sch"], prefix) & filters.me)
@with_reply
async def schedule_message(client: Client, message: Message):
    reply_msg = message.reply_to_message.id
    if len(message.command) > 2:
        chat_id = message.text.split(maxsplit=2)[1]
        schedule_time = message.text.split(maxsplit=2)[2]
        current_year = datetime.now().year
        try:
            schedule_date = datetime.strptime(
                f"{current_year}-{schedule_time}", "%Y-%m-%d %H:%M"
            )
            await client.copy_message(
                chat_id=chat_id,
                from_chat_id=message.chat.id,
                message_id=reply_msg,
                schedule_date=schedule_date,
            )
            await message.edit(
                f"<code>Message scheduled to {schedule_time} on {schedule_date.strftime('%d %B')}</code>"
            )
        except ChatForwardsRestricted:
            await message.edit(
                "<code>Current chat has restricted message copy/forwards.</code>"
            )
            return
        except ValueError:
            await message.edit(
                "<code>Invalid time format</code>\n<code>The correct format is 'MM-DD HH:MM'</code>"
            )
            return
    elif len(message.command) == 2:
        await message.edit("<code>Time not specified</code>")
    else:
        await message.edit("<code>Target not specified</code>")


# This adds instructions for your module
modules_help["messaging"] = {
    "dm [chat_id] [reply to message]*": "Send a message to a user.",
    "sch [chat_id] [time] [reply to message]*": "Schedule a message to a user.",
    "schedule [chat_id] [time] [reply to message]*": "Schedule a message to a user."
    "\n\n<b>chat_id</b> - Use the unique user ID or username of the target chat. For personal messages, use 'me' or 'self'. For contacts, use their phone number. For public links, use t.me/"
    "\n<b>time format:</b> MM-DD HH:MM",
}
