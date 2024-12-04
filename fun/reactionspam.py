import asyncio, random
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
    await message.edit(f"<b>One moment...</b>", parse_mode=enums.ParseMode.HTML)
    try:
        selected_emojis = random.sample(emojis, 3)
        print(selected_emojis)
        await client.send_reaction(
            message.chat.id,
            message_id=message.reply_to_message.id,
            emoji=selected_emojis,
        )
        await message.delete()
    except Exception as e:
        return await message.edit_text(format_exc(e))


modules_help["reactionspam"] = {"reactspam [amount]* [emoji]*": "spam reactions"}
