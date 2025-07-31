import asyncio

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("tagall", prefix) & filters.me)
async def tagall(client: Client, message: Message):
    await message.delete()
    chat_id = message.chat.id
    string = ""
    limit = 1
    icm = client.get_chat_members(chat_id)
    async for member in icm:
        tag = member.user.username
        if limit <= 5:
            string += f"@{tag}\n" if tag != None else f"{member.user.mention}\n"
            limit += 1
        else:
            await client.send_message(
                chat_id, text=string, parse_mode=enums.ParseMode.HTML
            )
            limit = 1
            string = ""
            await asyncio.sleep(2)


@Client.on_message(filters.command("hidetagall", prefix) & filters.me)
async def hidetagall(client: Client, message: Message):
    chat_id = message.chat.id
    
    original_text = message.text or message.caption or ""
    command_parts = original_text.split(maxsplit=1)
    remaining_text = command_parts[1] if len(command_parts) > 1 else ""
    
    hidden_mentions = ""
    member_count = 0
    max_members = 100
    
    try:
        icm = client.get_chat_members(chat_id)
        async for member in icm:
            if member_count >= max_members:
                break
            if not member.user.is_bot and not member.user.is_deleted:
                hidden_mentions += f'<a href="tg://user?id={member.user.id}">‍</a> '
                member_count += 1
    except Exception as e:
        await message.edit_text(f"Error getting members: {str(e)}")
        return
    
    final_text = hidden_mentions + remaining_text
    
    try:
        if message.media:
            await message.edit_caption(final_text, parse_mode=enums.ParseMode.HTML)
        else:
            await message.edit_text(final_text, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        if message.media:
            await message.delete()
            await client.send_message(chat_id, final_text, parse_mode=enums.ParseMode.HTML)
        else:
            await message.edit_text(f"Error editing message: {str(e)}")


modules_help["tagall"] = {
    "tagall": "Tag all members visibly",
    "hidetagall [text/media]": "Tag all members invisibly with hidden characters",
}
