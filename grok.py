import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

# Grok API details
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_API_KEY = "Grok API Key"

async def fetch_grok_response(query: str, message: Message, reply=False):
    """Fetches response from the Grok API and sends it back to the user."""
    response_msg = await message.reply("<code>Umm, lemme think...</code>") if reply else await message.edit("<code>Umm, lemme think...</code>")
    
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # The payload structure based on the provided `curl` command
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0
    }
    
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "No answer found.")

        response_content = f"**Question:**\n{query}\n**Answer:**\n{response_text}"
        
        if reply:
            await response_msg.edit_text(response_content, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await message.edit(response_content, parse_mode=enums.ParseMode.MARKDOWN)

    except requests.exceptions.RequestException as e:
        await response_msg.edit_text("An error occurred, please try again later.") if reply else await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["grok"], prefix))
async def grok(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `grok <query>`")
        return
    
    query = " ".join(message.command[1:])
    await fetch_grok_response(query, message, reply=not message.from_user.is_self)

modules_help["grok"] = {
    "grok [query]*": "Ask anything to Grok AI",
}
