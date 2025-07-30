from pyrogram import Client, filters, enums
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
    
    chunk_size = 4080 
    
    if len(json_data) <= chunk_size:
        await client.send_message(
            "me",
            f"```json\n{json_data}\n```",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        chunks = [json_data[i:i+chunk_size] for i in range(0, len(json_data), chunk_size)]
        
        for chunk in chunks:
            await client.send_message(
                "me",
                f"```json\n{chunk}\n```",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            
    await message.delete()

modules_help["raw_json"] = {
    "raw [reply]": "Get raw JSON data of replied message and send to saved messages",
}
