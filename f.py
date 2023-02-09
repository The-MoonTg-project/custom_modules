from os import remove
from random import randint

from pyrogram import Client, filters

from utils.misc import modules_help, prefix
from utils.scripts import import_library

wget = import_library("wget")


def download_sticker(url):
    wget.download(url, "f.webp")


@Client.on_message(filters.command(["f"], prefix) & filters.me)
async def random_stiker(client, message):
    await message.delete()
    random = randint(1, 63)
    index = f"00{random}" if random < 10 else f"0{random}"
    sticker = (
        f"https://www.chpic.su/_data/stickers/f/FforRespect/FforRespect_{index}.webp"
    )
    download_sticker(sticker)
    await client.send_sticker(chat_id=message.chat.id, sticker="f.webp")
    remove("f.webp")


modules_help["f"] = {
    "f": "Send f to pay respect",
}
