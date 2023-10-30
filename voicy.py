# original module voicy: https://raw.githubusercontent.com/ahmedov777-ai/custom_modules/main/voicy.py
# author: @THE_BURGERNET777 in telegram

import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import with_reply, format_exc


@Client.on_message(filters.command(["vo", "voicy"], prefix) & filters.me)
@with_reply
async def voice_text(client: Client, message: Message):
    try:
        if message.reply_to_message.voice:
            await message.edit("<b>Wait...</b>",parse_mode=enums.ParseMode.HTML)
            await client.unblock_user("@voicybot")
            await message.reply_to_message.forward("@voicybot")
            await asyncio.sleep(5)
            messages = await client.get_history("@voicybot", limit=1)
            await client.read_history("@voicybot")
            text = (
                messages[0]
                .text.replace(
                    "Путин и его свита убивают мирное население на войне в Украине #stopputin",
                    "",
                    parse_mode=enums.ParseMode.HTML
                )
                .replace(
                    "Putin and his cronies kill civilians in the war in Ukraine #stopputin",
                    "",
                    parse_mode=enums.ParseMode.HTML
                )
            )
            await message.edit(f"<b>Text: {text}</b>",parse_mode=enums.ParseMode.HTML)
        else:
            await message.edit("<b>It's not a voice</b>",parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.edit(format_exc(e),parse_mode=enums.ParseMode.HTML)


modules_help["voicy"] = {"voicy [reply]*": "get text from voice"}
