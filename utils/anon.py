import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("anon", prefix) & filters.me)
async def anon(client: Client, message: Message):
   if len(message.command) <= 2:
       return
   
   try:
       target_chat_id = int(message.command[1])
       text_content = " ".join(message.command[2:])
       
       await message.delete()
       
       if message.reply_to_message:
           if message.reply_to_message.media:
               if message.reply_to_message.photo:
                   sent_msg = await client.send_photo(
                       target_chat_id,
                       message.reply_to_message.photo.file_id,
                       caption=text_content if text_content else None
                   )
               elif message.reply_to_message.video:
                   sent_msg = await client.send_video(
                       target_chat_id,
                       message.reply_to_message.video.file_id,
                       caption=text_content if text_content else None
                   )
               elif message.reply_to_message.document:
                   sent_msg = await client.send_document(
                       target_chat_id,
                       message.reply_to_message.document.file_id,
                       caption=text_content if text_content else None
                   )
               elif message.reply_to_message.audio:
                   sent_msg = await client.send_audio(
                       target_chat_id,
                       message.reply_to_message.audio.file_id,
                       caption=text_content if text_content else None
                   )
               elif message.reply_to_message.voice:
                   sent_msg = await client.send_voice(
                       target_chat_id,
                       message.reply_to_message.voice.file_id,
                       caption=text_content if text_content else None
                   )
               elif message.reply_to_message.sticker:
                   sent_msg = await client.send_sticker(
                       target_chat_id,
                       message.reply_to_message.sticker.file_id
                   )
                   if text_content:
                       await client.send_message(target_chat_id, text_content)
               else:
                   sent_msg = await client.send_message(target_chat_id, text_content)
           else:
               reply_text = message.reply_to_message.text or message.reply_to_message.caption
               full_text = f"{reply_text}\n\n{text_content}" if reply_text and text_content else (reply_text or text_content)
               sent_msg = await client.send_message(target_chat_id, full_text)
       else:
           sent_msg = await client.send_message(target_chat_id, text_content)
       
       await client.forward_messages(
           message.chat.id,
           target_chat_id,
           sent_msg.id
       )
       
   except ValueError:
       await message.edit("Invalid chat ID format")
       await asyncio.sleep(2)
       await message.delete()
   except Exception as e:
       await message.edit(f"Error: {str(e)}")
       await asyncio.sleep(3)
       await message.delete()

modules_help["anonymous"] = {
   "anon [chat_id] [message]*": "send anonymous message to specified chat ID and forward back\n"
   "Reply to media to send it anonymously\n"
   "Usage: anon -1001234567890 Hello world"
}
