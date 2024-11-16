import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.db import db

GROK_API_URL = "https://api.x.ai/v1/chat/completions"


@Client.on_message(filters.command("set_grokapi", prefix) & filters.me)
async def set_grok_api(_, message: Message):
    if len(message.command) < 2:
        await message.reply(f"Usage: {prefix}set_grokapi <api_key>")
        return

    new_api_key = message.text.split(maxsplit=1)[1]

    headers = {"Authorization": f"Bearer {new_api_key}", "Content-Type": "application/json"}
    test_payload = {
        "messages": [{"role": "system", "content": "Test message"}],
        "model": "grok-beta",
        "stream": False,
    }

    try:
        test_response = requests.post(GROK_API_URL, headers=headers, json=test_payload, timeout=10)
        test_response.raise_for_status()
        db.set("custom.grok", "api_key", new_api_key)
        await message.edit_text("Grok API key set and validated successfully!")

    except requests.exceptions.RequestException:
        await message.edit_text("Failed to validate the API key. Please try again.")


async def fetch_grok_response(query: str, message: Message, reply=False):
    response_msg = await (
        message.reply("<code>Thinking... please wait.</code>")
        if reply
        else message.edit("<code>Thinking... please wait.</code>")
    )

    grok_api_key = db.get("custom.grok", "api_key", None)
    if not grok_api_key:
        return await response_msg.edit_text("Grok API key is not set. Use /set_grokapi to set it.")

    headers = {
        "Authorization": f"Bearer {grok_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0,
    }

    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        response_text = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "I'm sorry, I couldn't find an answer.")
        )

        response_content = f"**Question:**\n{query}\n**Answer:**\n{response_text}"

        await response_msg.edit_text(response_content, parse_mode=enums.ParseMode.MARKDOWN)

    except requests.exceptions.RequestException as e:
        await response_msg.edit_text(f"An error occurred: {str(e)}")


@Client.on_message(filters.command("grok", prefix))
async def grok(_, message: Message):
    if len(message.command) < 2:
        if message.from_user.is_self:
            await message.edit(f"Usage: {prefix}grok <query>")
        else:
            await message.reply(f"Usage: {prefix}grok <query>")
        return

    query = " ".join(message.command[1:]).strip()
    await fetch_grok_response(query, message, reply=not message.from_user.is_self)


modules_help["grokai"] = {
    "grok [query]*": "Ask anything to Grok AI.",
    "set_grokapi [api_key]*": "Set or update the Grok API key.",
}
