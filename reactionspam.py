import asyncio
from pyrogram import Client, filters, enums
from pyrogram.raw import functions
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

emojis = [
    "👍",
    "👎",
    "❤️",
    "🔥",
    "🥰",
    "👏",
    "😁",
    "🤔",
    "🤯",
    "😱",
    "🤬",
    "😢",
    "🎉",
    "🤩",
    "🤮",
    "💩",
]


@Client.on_message(filters.command("reactspam", prefix) & filters.me)
async def reactspam(client: Client, message: Message):
    if len(message.command) > 1:
        intam = message.text.split(None, 2)[1]
        amount = int(intam)
    else:
        message.edit_text("amount not given")
    if len(message.command) > 2:
        reaction = message.text.split(None, 2)[2]
    else:
        message.edit_text("reaction not given")
    await message.edit(f"<b>One moment...</b>", parse_mode=enums.ParseMode.HTML)
    for i in range(amount):
        if reaction in emojis:
            try:
                await client.send_reaction(
                    message.chat.id, message.id - i, reaction
                )
            except Exception as e:
                return await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)
        else:
            return await message.edit(f"<b>You can't use that emoji...</b>", parse_mode=enums.ParseMode.HTML)
    await message.edit(f"<b>Done!</b>", parse_mode=enums.ParseMode.HTML)


modules_help["reactionspam"] = {"reactspam [amount]* [emoji]*": "spam reactions"}
