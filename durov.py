from random import randint

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("durov", prefix) & filters.me)
async def durov(_, message: Message):
    await message.edit(
        f"<b>Random post from channel: https://t.me/durov/{randint(21, 36500)}</b>"
    )


modules_help["durov"] = {"bugurut": "Send random post from durov channel"}
