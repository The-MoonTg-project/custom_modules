from pyrogram import Client, filters
from pyrogram.types import Message
import json

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("raw", prefix) & filters.me)
async def get_raw_message(client: Client, message: Message):
    if not message.reply_to_message:
        await message.delete()
        return
    
    raw_data = str(message.reply_to_message)
    json_data = json.dumps(json.loads(raw_data), indent=2, ensure_ascii=False)
    
    chunk_size = 4096 - 10
    
    if len(json_data) <= chunk_size:
        await client.send_message("me", f"```json\n{json_data}\n```", parse_mode="markdown")
    else:
        chunks = [json_data[i:i+chunk_size] for i in range(0, len(json_data), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                await client.send_message("me", f"```json\n{chunk}", parse_mode="markdown")
            elif i == len(chunks) - 1:
                await client.send_message("me", f"{chunk}\n```", parse_mode="markdown")
            else:
                await client.send_message("me", chunk, parse_mode="markdown")
    
    await message.delete()


modules_help["raw_json"] = {
    "raw [reply]": "Get raw JSON data of replied message and send to saved messages",
}
