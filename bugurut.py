from random import randint

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("bugurut", prefix) & filters.me)
async def bugurut(_, message: Message):
    await message.edit(
        f"<b>Random post from channel: https://t.me/bugurtthread/{randint(21, 36500)}</b>"
    )


modules_help["bugurut"] = {"bugurut": "Send random post from bugurt channel"}
