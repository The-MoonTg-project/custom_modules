import uuid
import re
from aiohttp import ClientSession
from httpx import AsyncClient, Timeout 
from aiohttp import FormData
from pyrogram import filters, types, enums, errors
import os
from utils.misc import modules_help, prefix
import base64
import requests


session = ClientSession()



def id_generator() -> str:
    return str(uuid.uuid4())

@Client.on_message(filters.command(["bboxai", "blackbox"], prefix) & filters.me)
async def blackbox(client, message):
    m = message
    msg = await m.reply_text("🔍")
    
    if len(m.text.split()) == 1:
        return await msg.edit_text(
            "Type some query buddy 🐼\n"
            "/blackbox text with reply to the photo or just text"
        )
    else:
        prompt = m.text.split(maxsplit=1)[1]
        user_id = id_generator()
        image = None
        
        if m.reply_to_message and (m.reply_to_message.photo or (m.reply_to_message.sticker and not m.reply_to_message.sticker.is_video)):
            file_name = f'blackbox_{m.chat.id}.jpeg'
            file_path = await m.reply_to_message.download(file_name=file_name)
            with open(file_path, 'rb') as file:
                image = file.read()
        
        if image:
            data = FormData()
            data.add_field('fileName', file_name)
            data.add_field('userId', user_id)
            data.add_field('image', image, filename=file_name, content_type='image/jpeg')
            api_url = "https://www.blackbox.ai/api/upload"
            try:
                async with session.post(api_url, data=data) as response:
                    response_json = await response.json()
            except Exception as e:
                return await msg.edit(
                    f"❌ Error: {str(e)}"
                )
            
            messages = [
                {
                    "role": "user", 
                    "content": response_json['response'] + "\n#\n" + prompt
                }
            ]
            data = {
                "messages": messages,
                "user_id": user_id,
                "codeModelMode": True,
                "agentMode": {},
                "trendingAgentMode": {},
            }
            headers = {"Content-Type": "application/json"}
            url = "https://www.blackbox.ai/api/chat"
            try:
                async with session.post(url, headers=headers, json=data) as response:
                    response_text = await response.text()
            except Exception as e:
                return await msg.edit(
                    f"❌ Error: {str(e)}"
                )
            
            cleaned_response_text = re.sub(r'^\$?@?\$?v=undefined-rv\d+@?\$?|\$?@?\$?v=v\d+\.\d+-rv\d+@?\$?', '', response_text)
            text = cleaned_response_text.strip()[2:]
            if "$~~~$" in text:
                text = re.sub(r'\$~~~\$.*?\$~~~\$', '', text, flags=re.DOTALL)
            rdata = {'reply': text}
        
            return await msg.edit_text(
                text=rdata['reply']
            )
        else:
            reply = m.reply_to_message
            if reply and reply.text:
                prompt = f"Old conversation:\n{reply.text}\n\nQuestion:\n{prompt}"
            messages = [
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            data = {
                "messages": messages,
                "user_id": user_id,
                "codeModelMode": True,
                "agentMode": {},
                "trendingAgentMode": {},
            }
            headers = {"Content-Type": "application/json"}
            url = "https://www.blackbox.ai/api/chat"
            try:
                async with session.post(url, headers=headers, json=data) as response:
                    response_text = await response.text()
            except Exception as e:
                return await msg.edit(
                    f"❌ Error: {str(e)}"
                )
            
            cleaned_response_text = re.sub(r'^\$?@?\$?v=undefined-rv\d+@?\$?|\$?@?\$?v=v\d+\.\d+-rv\d+@?\$?', '', response_text)
            text = cleaned_response_text.strip()[2:]
            if "$~~~$" in text:
                text = re.sub(r'\$~~~\$.*?\$~~~\$', '', text, flags=re.DOTALL)
            rdata = {'reply': text}
            
            return await msg.edit_text(
                text=rdata['reply']
            )



@Client.on_message(filters.command(["imgur"], prefix) & filters.me)
async def imgur(client, message):
    # Check if a reply exists
    msg = await message.reply_text(
      "🎉 Please patience. trying to upload..."
    )
    if message.reply_to_message and message.reply_to_message.photo:
        # Download the photo
        photo_path = await message.reply_to_message.download()
        # Read the photo file and encode as base64
        with open(photo_path, "rb") as file:
            data = file.read()
            base64_data = base64.b64encode(data)
        # Set API endpoint and headers for image upload
        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": "Client-ID a10ad04550b0648"}
        # Upload image to Imgur and get URL
        response = requests.post(url, headers=headers, data={"image": base64_data})
        result = response.json()
        await msg.edit_text(result["data"]["link"])
    elif message.reply_to_message and message.reply_to_message.animation:
        # Download the animation (GIF)
        animation_path = await message.reply_to_message.download()
        # Read the animation file and encode as base64
        with open(animation_path, "rb") as file:
            data = file.read()
            base64_data = base64.b64encode(data)
        # Set API endpoint and headers for animation upload
        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": "Client-ID a10ad04550b0648"}
        # Upload animation to Imgur and get URL
        response = requests.post(url, headers=headers, data={"image": base64_data})
        result = response.json()
        await msg.edit_text(result["data"]["link"])
    else:
        await msg.edit_text("Please reply to a photo or animation (GIF) to upload to Imgur.")




modules_help["sarethai"] = {
    "blackbox [query]*": "Ask anything to Blackbox",
    "bbox [query]*": "Ask anything to Blackbox",
    "imgur [img]*": "upload umg to imgur",
            
