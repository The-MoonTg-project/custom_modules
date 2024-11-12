import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.db import db

GROK_API_URL = "https://api.x.ai/v1/chat/completions"


@Client.on_message(filters.command("set_grokapi", prefix) & filters.me)
async def set_grokapi(_, message: Message):
    OCR_SPACE_API_KEY = db.get("custom.grok", "grokapi", None)
    if OCR_SPACE_API_KEY is not None:
        return await message.edit_text(f"grokapi key is already set")
    if len(message.command) > 1:
        api_key = message.text.split(maxsplit=1)[1]
        db.set("custom.grok", "grokapi", api_key)
        return await message.edit_text(f"grokapi key set success")


async def fetch_grok_response(query: str, message: Message, reply=False):
    """Fetches response from the Grok API and sends it back to the user."""
    response_msg = (
        await message.reply("<code>Umm, lemme think...</code>")
        if reply
        else await message.edit("<code>Umm, lemme think...</code>")
    )

    GROK_API_KEY = db.get("custom.grok", "grokapi", None)
    if GROK_API_KEY is None:
        return await message.edit_text(f"grokapi key is not set")

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
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
        response = requests.post(GROK_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        response_text = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "No answer found.")
        )

        response_content = f"**Question:**\n{query}\n**Answer:**\n{response_text}"

        if reply:
            await response_msg.edit_text(
                response_content, parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit(response_content, parse_mode=enums.ParseMode.MARKDOWN)

    except requests.exceptions.RequestException as e:
        await response_msg.edit_text(
            "An error occurred, please try again later."
        ) if reply else await message.edit("An error occurred, please try again later.")


@Client.on_message(filters.command("grok", prefix))
async def grok(_, message: Message):
    if len(message.command) < 2:
        await message.reply(f"Usage: {prefix}grok <query>")
        return

    query = " ".join(message.command[1:])
    await fetch_grok_response(query, message, reply=not message.from_user.is_self)


modules_help["grokai"] = {
    "grok [query]*": "Ask anything to Grok AI",
    "set_grokapi [api_key]*": "Set Grok API key",
}
