import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("tdel", prefix) & filters.me)
async def tdel_message(_, message: Message):
    if len(message.command) <= 2:
        await message.edit(
            "<b>Error:</b> <i>You must specify time (seconds) and message text</i>\n"
            "<b>Example:</b> <code>.tdel 10 Hello everyone!</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(5)
        await message.delete()
        return
    
    try:
        delete_time = int(message.command[1])
        text = " ".join(message.command[2:])
        
        if delete_time <= 0:
            await message.edit(
                "<b>Error:</b> <i>Time must be a positive number!</i>",
                parse_mode=enums.ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            return
            
        if delete_time > 86400:
            await message.edit(
                "<b>Error:</b> <i>Maximum time is 24 hours (86400 seconds)!</i>",
                parse_mode=enums.ParseMode.HTML,
            )
            await asyncio.sleep(5)
            await message.delete()
            return
        
        if not text.strip():
            await message.edit(
                "<b>Error:</b> <i>Message text cannot be empty!</i>",
                parse_mode=enums.ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            return
        
        await message.edit(
            text,
            parse_mode=enums.ParseMode.HTML,
        )
        
        await asyncio.sleep(delete_time)
        await message.delete()
        
    except ValueError:
        await message.edit(
            "<b>Error:</b> <i>Time must be an integer!</i>\n"
            "<b>Example:</b> <code>.tdel 30 This message will be deleted in 30 seconds</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.edit(
            f"<b>Unexpected error:</b> <code>{str(e)}</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(5)
        await message.delete()

modules_help["timed_delete"] = {
    "tdel [time] [text]*": "send self-deleting message\n"
    "time: seconds until deletion\n"
    "text: message content\n"
    "example: .tdel 60 this message will delete in one minute"
}
