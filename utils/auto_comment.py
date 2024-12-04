from contextlib import suppress
from pyrogram import Client, filters, ContinuePropagation, enums
from pyrogram.types import Message
from pyrogram.errors import MsgIdInvalid
from utils.misc import modules_help, prefix
from utils.db import db


@Client.on_edited_message(filters.channel)
async def send_comment(client: Client, message: Message):
    enabled = db.get("custom.auto_comment", "enabled", False)
    with suppress(MsgIdInvalid):
        if enabled:
            msg = await client.get_discussion_message(message.chat.id, message.id)
            await msg.reply(
                db.get("custom.auto_comment", "text"), parse_mode=enums.ParseMode.HTML
            )
    raise ContinuePropagation


@Client.on_message(filters.command(["auto_comment", "ac"], prefix) & filters.me)
async def auto_comment(_, message: Message):
    if len(message.command) > 1:
        comment = message.text.split(maxsplit=1)[1]
        db.set("custom.auto_comment", "enabled", True)
        db.set("custom.auto_comment", "text", comment)

        await message.edit(
            f"<b>Auto comment enabled\nComment:</b> <code>{comment}</code>",
            parse_mode=enums.ParseMode.HTML,
        )
    else:
        db.set("custom.auto_comment", "enabled", False)
        await message.edit(
            "<b>Auto comment disabled</b>", parse_mode=enums.ParseMode.HTML
        )


modules_help["auto_comment"] = {
    "auto_comment [text]*": "enable auto-reply to posts in channels. Running without text equals to disable"
}
