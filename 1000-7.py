from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

digits = {
    str(i): el
    for i, el in enumerate(
        ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    )
}


def prettify(val: int) -> str:
    return "".join(digits[i] for i in str(val))


@Client.on_message(filters.command("ghoul", prefix) & filters.me)
async def ghoul_counter(_, message: Message):
    await message.delete()

    if len(message.command) > 1 and message.command[1].isdigit():
        counter = int(message.command[1])
    else:
        counter = 1000

    msg = await message.reply(prettify(counter), quote=False)

    await sleep(1)

    while counter // 7:
        counter -= 7
        await msg.edit(prettify(counter))
        await sleep(1)

    await msg.edit("<b>🤡 ГУЛЬ 🤡</b>")


modules_help["1000-7"] = {
    "ghoul [count_from]": "counting from 1000 (or given [count_from] to 0 as a ghoul"
}
