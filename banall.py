from pyrogram import Client, filters, enums

from pyrogram.types import *
import asyncio
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from pyrogram.errors.exceptions.flood_420 import FloodWait
import asyncio
import os
import os

@Client.on_message(filters.command("banall", prefix) & filters.me)
async def banall(client: Client, message: Message):
    group_id = message.command[1]
    chat_id = int(group_id)

    async for i in client.get_chat_members(chat_id):
        message.edit_text(f"getting memebers from {chat_id}")
    async for i in client.get_chat_members(chat_id):
        try:
            await client.ban_chat_member(chat_id,user_id=i.user.id)
            message.edit_text("kicked lol, I'm the Devil 😈")
        except FloodWait as e:
            await asyncio.sleep(e.x)
            print(e)
        except Exception as e:
            message.edit_text(" failed af 😭")
    print("process completed")
    
    
modules_help["banall"] = {
    "banall [group id]*": "ban all members ^⁠_⁠^",
}
