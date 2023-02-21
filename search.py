from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix

# noinspection PyUnresolvedReferences
from utils.scripts import format_exc

now = {}


@Client.on_message(filters.command(["search"], prefix) & filters.me)
async def search_cmd(client: Client, message: Message):
    if now.get(message.chat.id):
        return await message.edit(
            "<b>You already have a search in progress!\n"
            "Type: <code>{}scancel</code> to cancel it.</b>".format(prefix)
        )

    await message.edit("<b>Start searching...</b>")
    finished = False
    local = False
    try:
        cmd = message.command[1]
        word = message.command[2].lower()
        timeout = float(message.command[3]) if len(message.command) > 3 else 2
    except:
        return await message.edit(
            "<b>Usage:</b> <code>{}search [/cmd]* [search_word]* [timeout=2.0]</code>".format(
                prefix
            )
        )

    now[message.chat.id] = True

    try:
        await message.reply_text(quote=False, text=cmd, reply_to_message_id=None)
        while not finished and now[message.chat.id]:
            async for msg in client.iter_history(message.chat.id, limit=2):
                if msg.from_user.id == message.from_user.id:
                    continue
                elif word in msg.text.lower():
                    finished = True
                    local = True
            if not local:
                await sleep(timeout)
                await message.reply_text(quote=False, text=cmd, reply_to_message_id=None)
            else:
                break
        if now[message.chat.id]:
            await message.reply_text("<b>Search finished!</b>")
    except Exception as ex:
        await message.edit(format_exc(ex))
    now[message.chat.id] = False


@Client.on_message(filters.command(["scancel"], prefix) & filters.me)
async def scancel_cmd(_: Client, message: Message):
    if not now.get(message.chat.id):
        return await message.edit("<b>There is no search in progress!</b>")
    now[message.chat.id] = False
    await message.edit("<b>Search cancelled!</b>")


modules_help["search"] = {
    "search [/cmd]* [search_word]* [timeout=2.0]": "Search for a specific word in bot (while)",
    'scancel': 'Cansel current search',
}
