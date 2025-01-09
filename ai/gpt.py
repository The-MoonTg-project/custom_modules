from utils.misc import modules_help, prefix
import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from datetime import datetime as dt

import logging
from utils.scripts import import_library

g4f = import_library("g4f")

from g4f.client import Client as Clients_g4f
logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGS = logging.getLogger("[toolsbot]")
owner_base = f"""
Your name is 🌝 moon ai bot. A kind and friendly AI assistant that answers in
a short and concise answer. Give short step-by-step reasoning if required.
- Powered by @KyuBtauMai on telegram
Today is {dt.now():%A %d %B %Y %H:%M}
"""
async def chat_message(question):
    clients_x = Clients_g4f()
    response = clients_x.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": owner_base},
            {"role": "user", "content": question}
        ],
    )
    messager = response.choices[0].message.content
    return messager
    
@Client.on_message(filters.command("ask", prefix) & filters.me)
async def chatgpt(client: Client, message: Message):
    if len(message.command) > 1:
        prompt = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        prompt = message.reply_to_message.text
    else:
        return await message.reply_text("Give ask from CHATGPT-4O")
    try:
        messager = await chat_message(prompt)
        if len(messager) > 4096:
            with open("chat.txt", "w+", encoding="utf8") as out_file:
                out_file.write(messager)
            await message.reply_document(
                document="chat.txt",
                disable_notification=True
            )
            os.remove("chat.txt")
        else:
            await message.reply_text(messager)
    except Exception as e:
        LOGS.error(str(e))
        return await message.reply_text(str(e))



modules_help["gpt"] = {
    "ask": "ask gpt",
    
