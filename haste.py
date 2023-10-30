import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import with_reply

BASE = "https://www.toptal.com/developers/hastebin"


@Client.on_message(filters.command("haste", prefix) & filters.me)
@with_reply
async def haste(client: Client, message: Message):
    reply = message.reply_to_message

    if reply.text is None:
        return

    await message.delete()

    result = requests.post(
        "{}/documents".format(BASE), data=reply.text.encode("UTF-8")
    ).json()

    await message.reply(
        "{}/{}.py".format(BASE, result["key"]), reply_to_message_id=reply.message_id, parse_mode=enums.ParseMode.HTML
    )


modules_help["haste"] = {"haste": "reply to text will upload text to hastebin ;)"}
