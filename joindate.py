import asyncio
import os
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.raw import functions
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command("joindate", prefix) & filters.me)
async def joindate(client: Client, message: Message):
    await message.edit(f"<b>One moment...</b>", parse_mode=enums.ParseMode.HTML)
    members = []
    cgetmsg = await client.get_messages(message.chat.id, 1)

    async for m in client.get_chat_members(message.chat.id):
        joined_date = m.joined_date.timestamp() if m.joined_date else cgetmsg.date.timestamp() if cgetmsg.date else 0
        members.append(
            (
                m.user.first_name,
                joined_date,
            )
        )

    members.sort(key=lambda member: member[1])

    with open("joined_date.txt", "w", encoding="utf8") as f:
        f.write("Join Date      First Name\n")
        for member in members:
            f.write(
                str(datetime.fromtimestamp(member[1]).strftime("%y-%m-%d %H:%M"))
                + f" {member[0]}\n"
            )

    await message.delete()
    await client.send_document(message.chat.id, "joined_date.txt")
    os.remove("joined_date.txt")


modules_help["joindate"] = {
    "joindate": "Get a list of all chat members and sort them by the date they joined the group"
}
