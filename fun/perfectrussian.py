from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.scripts import with_reply

import random


@Client.on_message(filters.command("prus", prefix) & filters.me)
@with_reply
async def prussian_cmd(_, message: Message):
    words = [
        "сука",
        "нахуй",
        "блять",
        "блядь",
        "пиздец",
        "еблан",
        "уебан",
        "уебок",
        "пизда",
        "очко",
        "хуй",
    ]
    splitted = message.reply_to_message.text.split()

    for i in range(0, len(splitted), random.randint(2, 3)):
        for j in range(1, 2):
            splitted.insert(i, random.choice(words))

    await message.edit(" ".join(splitted), parse_mode=enums.ParseMode.HTML)


modules_help["perfectrussian"] = {
    "prus": "translate your message into perfect 🇷🇺Russian",
}
