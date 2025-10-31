import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

COPILOT_API_URL = "https://api.deline.web.id/ai/copilot?text="

async def fetch_copilot_response(query: str, message: Message, is_self: bool):
    response_msg = await (message.edit("<code>Thinking...</code>") if is_self else message.reply("<code>Thinking...</code>"))
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{COPILOT_API_URL}{query.strip()}") as resp:
                data = await resp.json()
        if data.get("status"):
            ai_response = data.get("result", "No response found.")
            formatted_response = f"**Question:**\n{query}\n\n**Answer:**\n{ai_response}"
        else:
            formatted_response = "Failed to fetch a response. Please try again."
        if len(formatted_response) > 4000:
            formatted_response = formatted_response[:4000] + "…"
        await response_msg.edit_text(formatted_response, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception:
        await response_msg.edit_text("An error occurred while connecting to the API. Please try again later.")

@Client.on_message(filters.command("copilot", prefix))
async def copilot_command(client: Client, message: Message):
    if message.reply_to_message and len(message.command) == 1:
        query = message.reply_to_message.text
    elif len(message.command) > 1:
        query = " ".join(message.command[1:])
    else:
        await message.reply(f"<b>Usage:</b> <code>{prefix}copilot [prompt]</code> or reply to a message with <code>{prefix}copilot</code>")
        return
    await fetch_copilot_response(query, message, message.from_user.is_self)

modules_help["copilot"] = {
    "copilot [query]*": "Ask anything to Copilot AI",
}
