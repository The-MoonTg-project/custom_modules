import os
import urllib.parse
from requests import get

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from utils import modules_help, prefix

WOLFRAM_ID = os.environ.get("WOLFRAM_ID", None)

@Client.on_message(filters.command("ask", prefix) & filters.me)
async def ask_cmd(client: Client, message: Message):
    if not WOLFRAM_ID:
        await message.edit("❌ **WOLFRAM_ID** is not set in your environment variables.")
        return

    input_text = ""
    if len(message.command) > 1:
        input_text = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        input_text = message.reply_to_message.text
        
    if not input_text:
        await message.edit(f"**Usage:** `{prefix}ask [question]` or reply to a question")
        return

    await message.edit("__Checking for your question in AI database...__")
    
    ques = urllib.parse.quote_plus(input_text)
    server = f"https://api.wolframalpha.com/v1/spoken?appid={WOLFRAM_ID}&i={ques}"
    
    try:
        res = get(server)
        if "Wolfram Alpha did not understand" in res.text:
            await message.edit("Oh! No, the AI system was not able to answer your question..")
            return
        
        await message.edit(f"**{input_text}**\n\n{res.text}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.edit(f"**Error:** `{e}`")

modules_help["ask"] = {
    "ask [question]": "Get Answers For The Questions using Wolfram Alpha :)"
}
