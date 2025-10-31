from pyrogram import Client, filters, enums  
from pyrogram.types import Message
import json
from utils.misc import modules_help, prefix

def send_chunked_messages(client, data, chat_id="me"):
    chunk_size = 4080
    
    if len(data) <= chunk_size:
        return [f"```json\n{data}\n```"]
    
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        chunks.append(f"```json\n{chunk}\n```")
    
    return chunks

@Client.on_message(filters.command("raw", prefix) & filters.me)
async def get_raw_message(client: Client, message: Message):
    if not message.reply_to_message:
        await message.delete()
        return
    
    raw_data = str(message.reply_to_message)
    json_data = json.dumps(json.loads(raw_data), indent=2, ensure_ascii=False)
    
    chunks = send_chunked_messages(client, json_data)
    
    for chunk in chunks:
        await client.send_message("me", chunk, parse_mode=enums.ParseMode.MARKDOWN)
            
    await message.delete()

@Client.on_message(filters.command("uraw", prefix) & filters.me)
async def get_user_raw_data(client: Client, message: Message):
    target_user = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    
    elif message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.MENTION:
                username = message.text[entity.offset:entity.offset + entity.length].replace('@', '')
                try:
                    target_user = await client.get_users(username)
                except:
                    continue
            elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                target_user = entity.user
    
    if not target_user:
        await message.edit("No user found to extract data. Reply to a message or mention a user.")
        return
    
    try:
        full_user = await client.get_users(target_user.id)
        raw_data = str(full_user)
        json_data = json.dumps(json.loads(raw_data), indent=2, ensure_ascii=False)
        
        chunks = send_chunked_messages(client, json_data)
        
        for chunk in chunks:
            await client.send_message("me", chunk, parse_mode=enums.ParseMode.MARKDOWN)
        
        await message.delete()
        
    except Exception as e:
        await message.edit(f"Error getting user data: {str(e)}")

@Client.on_message(filters.command("picraw", prefix) & filters.me)
async def get_profile_pics_raw(client: Client, message: Message):
    target_user = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    
    elif message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.MENTION:
                username = message.text[entity.offset:entity.offset + entity.length].replace('@', '')
                try:
                    target_user = await client.get_users(username)
                except:
                    continue
            elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                target_user = entity.user
    
    if not target_user:
        await message.edit("No user found to extract photos. Reply to a message or mention a user.")
        return
    
    try:
        photos = []
        async for photo in client.get_chat_photos(target_user.id):
            photos.append(photo)
        
        if not photos:
            await message.edit("This user has no profile photos.")
            return
        
        photo_data = []
        for i, photo in enumerate(photos):
            photo_info = {
                "index": i + 1,
                "file_id": photo.file_id,
                "file_unique_id": photo.file_unique_id,
                "date": photo.date.isoformat() if photo.date else None,
                "sizes": []
            }
            
            for size in photo.thumbs:
                size_info = {
                    "type": size.type if hasattr(size, 'type') else "unknown",
                    "width": size.width if hasattr(size, 'width') else None,
                    "height": size.height if hasattr(size, 'height') else None,
                    "file_size": size.file_size if hasattr(size, 'file_size') else None
                }
                photo_info["sizes"].append(size_info)
            
            photo_data.append(photo_info)
        
        json_data = json.dumps({
            "user_id": target_user.id,
            "username": target_user.username,
            "first_name": target_user.first_name,
            "last_name": target_user.last_name,
            "total_photos": len(photos),
            "photos": photo_data
        }, indent=2, ensure_ascii=False)
        
        chunks = send_chunked_messages(client, json_data)
        
        for chunk in chunks:
            await client.send_message("me", chunk, parse_mode=enums.ParseMode.MARKDOWN)
        
        await message.delete()
        
    except Exception as e:
        await message.edit(f"Error getting profile photos: {str(e)}")

modules_help["raw_json"] = {
    "raw [reply]": "Get raw JSON data of replied message and send to saved messages",
    "uraw [reply/mention]": "Get raw user data from replied or mentioned user",
    "picraw [reply/mention]": "Get file_id of all profile pictures from user",
}
