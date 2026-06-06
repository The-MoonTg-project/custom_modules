from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix

@Client.on_message(filters.command("hl", prefix) & filters.me)
async def hide_link(client: Client, message: Message):
    input_text = ""
    
    if len(message.command) > 1:
        input_text = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        input_text = message.reply_to_message.text
        
    if not input_text:
        await message.edit(f"**Usage:** `{prefix}hl [link]` or reply to a link")
        return

    await message.edit(
        f"[ㅤㅤㅤㅤㅤㅤㅤ]({input_text})", 
        disable_web_page_preview=True
    )

modules_help["hl"] = {
    "hl [link]": "To hide the url with white spaces using hyperlink. You can also reply to a link."
}
