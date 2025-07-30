import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("raw", prefix) & filters.me)
async def raw_message(client: Client, message: Message):
   if not message.reply_to_message:
       await message.edit("<code>Reply to a message to get its raw JSON</code>", parse_mode=enums.ParseMode.HTML)
       return
   
   try:
       raw_json = str(message.reply_to_message)
       
       if len(raw_json) > 4096:
           i = 0
           for x in range(0, len(raw_json), 4096):
               if i == 0:
                   sent_msg = await client.send_message(
                       "me",
                       f"<b>Raw JSON:</b>\n<code>{raw_json[x:x + 4096]}</code>",
                       parse_mode=enums.ParseMode.HTML,
                   )
               else:
                   await client.send_message(
                       "me",
                       f"<code>{raw_json[x:x + 4096]}</code>",
                       parse_mode=enums.ParseMode.HTML,
                   )
               i += 1
               await asyncio.sleep(0.18)
       else:
           sent_msg = await client.send_message(
               "me",
               f"<b>Raw JSON:</b>\n<code>{raw_json}</code>",
               parse_mode=enums.ParseMode.HTML,
           )
       
       await message.edit("<code>Raw JSON sent to Saved Messages</code>", parse_mode=enums.ParseMode.HTML)
       
   except Exception as e:
       await message.edit(f"<code>Error: {e}</code>", parse_mode=enums.ParseMode.HTML)

modules_help["raw"] = {
   "raw*": "get raw JSON of replied message and send it to Saved Messages"
}
