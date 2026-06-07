import os
import urllib.parse
from requests import get

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from utils import modules_help, prefix
from utils.db import db

@Client.on_message(filters.command("ask", prefix) & filters.me)
async def ask_cmd(client: Client, message: Message):
    wolfram_id = db.get("custom.ask", "WOLFRAM_ID") or os.environ.get("WOLFRAM_ID", None)
    
    if not wolfram_id:
        await message.edit(f"❌ **WOLFRAM_ID** is not set.\nSet it using `{prefix}setwolfram <id>` or set the WOLFRAM_ID environment variable.")
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
    server = f"https://api.wolframalpha.com/v1/spoken?appid={wolfram_id}&i={ques}"
    
    try:
        res = get(server)
        if "Wolfram Alpha did not understand" in res.text:
            await message.edit("Oh! No, the AI system was not able to answer your question..")
            return
        
        await message.edit(f"**{input_text}**\n\n{res.text}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.edit(f"**Error:** `{e}`")


@Client.on_message(filters.command("setwolfram", prefix) & filters.me)
async def set_wolfram(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit(f"**Usage:** `{prefix}setwolfram <your_wolfram_id>`")
        return
        
    wolfram_id = message.command[1]
    db.set("custom.ask", "WOLFRAM_ID", wolfram_id)
    await message.edit(f"✅ **WOLFRAM_ID** successfully saved to database.")


modules_help["ask"] = {
    "ask [question]": "Get Answers For The Questions using Wolfram Alpha :)",
    "setwolfram [id]": "Save your Wolfram Alpha App ID to the database"
}
