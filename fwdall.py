import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command(["fwdall"], prefix) & filters.me)
async def forward(client: Client, message: Message):
    sta = None if len(message.text.split(" ")) < 2 else message.text.split(" ")[1]
    if sta is not None:
        await message.edit("<b>Working...</b>")
        try:
            target = await client.get_chat(sta)
        except RPCError:
            await message.edit("<b>Unknown target.</b>")
            return
        msgs = []
        async for msg in client.iter_history(message.chat.id, reverse=True):
            msgs.append(msg.message_id)
            if len(msgs) >= 100:
                try:
                    await client.forward_messages(target.id, message.chat.id, msgs)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await client.forward_messages(target.id, message.chat.id, msgs)
                msgs = []
        if msgs:
            try:
                await client.forward_messages(target.id, message.chat.id, msgs)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await client.forward_messages(target.id, message.chat.id, msgs)
        await message.edit("<b>Done successfully.</b>")
    else:
        await message.edit("<b>No target passed.</b>")


modules_help["fwdall"] = {
    "fwdall [target]*": "forward all messages to defined target [username/chat_id/chat_link]"
}
