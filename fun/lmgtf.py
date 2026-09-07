import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from utils import modules_help, prefix


@Client.on_message(filters.command("lmgtf", prefix) & filters.me)
async def lmgtf_cmd(client: Client, message: Message):
    query = ""
    if len(message.command) > 1:
        query = " ".join(message.command[1:])
    elif message.reply_to_message and message.reply_to_message.text:
        query = message.reply_to_message.text

    if not query:
        await message.edit(
            "`Provide a search query or reply to a text message. Example:` `.lmgtf how to do something in water`"
        )
        return
    encoded_query = urllib.parse.quote_plus(query)

    # Base URL for let me google that for you
    long_url = f"https://lmgtfy.com/?q={encoded_query}"

    text = f"[Here is your answer]({long_url})\n`{long_url}`"

    await message.edit(
        text, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN
    )


modules_help["lmgtf"] = {
    "lmgtf [query]": "Generates an unshortened 'Let Me Google That For You' link for the given query."
}
