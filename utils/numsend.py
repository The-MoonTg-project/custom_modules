import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("numsend", prefix) & filters.me)
async def numsend(client: Client, message: Message):
   if len(message.command) <= 2:
       return
   
   try:
       user_id = int(message.command[1])
       text = " ".join(message.command[2:])
       
       if message.reply_to_message:
           if message.reply_to_message.media:
               await client.copy_message(
                   chat_id=user_id,
                   from_chat_id=message.chat.id,
                   message_id=message.reply_to_message.id,
                   caption=text if text else None
               )
           else:
               await client.send_message(
                   chat_id=user_id,
                   text=text if text else message.reply_to_message.text
               )
       else:
           await client.send_message(chat_id=user_id, text=text)
       
       await message.delete()
       
   except ValueError:
       await message.edit("Invalid user ID format", parse_mode=enums.ParseMode.HTML)
   except Exception as e:
       await message.edit(f"Error: <code>{e}</code>", parse_mode=enums.ParseMode.HTML)

modules_help["numsend"] = {
   "numsend [user_id] [message]*": "send message to user by numeric ID\n"
   "Reply to media to forward it with optional caption\n"
   "Original message will be deleted after sending"
}
