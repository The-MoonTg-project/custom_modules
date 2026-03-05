import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.scripts import with_reply

from utils import modules_help, prefix

BASE = "https://hastebin.com"

headers = {"Authorization": "Bearer YOURTOKEN"}


@Client.on_message(filters.command("haste", prefix) & filters.me)
@with_reply
async def haste(client: Client, message: Message):
    reply = message.reply_to_message

    if reply.text is None:
        return

    await message.delete()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE}/documents",
                data=reply.text.encode("UTF-8"),
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
    except aiohttp.ClientResponseError as http_err:
        await message.reply(f"HTTP error occurred: {http_err}")
        return
    except aiohttp.ClientError as err:
        await message.reply(f"Error occurred: {err}")
        return
    except ValueError:
        await message.reply("Error: Response is not in JSON format.")
        return

    await message.reply(
        "{}/{}.py".format(BASE, result["key"]),
        reply_to_message_id=reply.message_id,
    )


modules_help["haste"] = {"haste": "reply to text will upload text to hastebin ;)"}
