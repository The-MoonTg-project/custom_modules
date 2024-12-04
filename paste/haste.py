import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import with_reply

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
        response = requests.post(
            "{}/documents".format(BASE),
            data=reply.text.encode("UTF-8"),
            headers=headers,
        )
        response.raise_for_status()  # Raises an HTTPError if the response was unsuccessful
        result = response.json()
    except requests.exceptions.HTTPError as http_err:
        await message.reply(f"HTTP error occurred: {http_err}")
        return
    except requests.exceptions.RequestException as err:
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
