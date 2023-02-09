from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command(["block"], prefix) & filters.me)
async def block_True(client: Client, message: Message):
    try:
        user_id = (
            message.command[1]
            if len(message.command) > 1
            else message.reply_to_message.from_user.id
        )
        await client.block_user(user_id)
        await message.edit(
            f"<b>🤡 The <a href='tg://user?id={user_id}'>user</a> is now blacklisted!</b>"
        )
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command(["unblock"], prefix) & filters.me)
async def unblock(client: Client, message: Message):
    try:
        user_id = (
            message.command[1]
            if len(message.command) > 1
            else message.reply_to_message.from_user.id
        )
        await client.unblock_user(user_id)
        await message.edit(
            f"<b>☺️ <a href='tg://user?id={user_id}'>User</a> removed from the blacklist!</b>"
        )
    except Exception as e:
        await message.edit(format_exc(e))


modules_help["blacklist"] = {
    "block [id|reply]*": "block user",
    "unblock [id|reply]*": "unblock user",
}
