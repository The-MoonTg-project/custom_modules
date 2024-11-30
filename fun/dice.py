from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc
import asyncio


@Client.on_message(filters.command("dice", prefix) & filters.me)
async def dice_text(client: Client, message: Message):
    try:
        value = int(message.command[1])
        if value not in range(1, 7):
            raise AssertionError
    except (ValueError, IndexError, AssertionError):
        return await message.edit(
            "<b>Invalid value</b>", parse_mode=enums.ParseMode.HTML
        )

    try:
        message.dice = type("bruh", (), {"value": 0})()
        while message.dice.value != value:
            message = (
                await asyncio.gather(
                    message.delete(), client.send_dice(message.chat.id)
                )
            )[1]
    except Exception as e:
        await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)


modules_help["dice"] = {
    "dice [1-6]*": "Generate dice with specified value. Works only in groups"
}
