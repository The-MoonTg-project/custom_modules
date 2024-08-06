from pyrogram import Client, filters

import requests

from utils.misc import prefix, modules_help


def get_completion(prompt):
    url = "https://www.samirxpikachu.run.place/Mixtral/142B"
    params = {"prompt": prompt}

    response = requests.get(url, params=params)
    response_json = response.json()

    return {
        "content": response_json.get("content", "No response from LLM"),
        "prompt_tokens": response_json.get("prompt_tokens", 0),
        "completion_tokens": response_json.get("completion_tokens", 0),
        "total_tokens": response_json.get("total_tokens", 0),
    }


@Client.on_message(filters.command("midai", prefix) & filters.me)
async def handle_message(client, message):
    if len(message.command) < 2:
        await message.reply_text("No Prompt provided.")
        return

    await message.edit_text("Processing...")
    # Extract the prompt text from the message
    prompt_text = message.text.split(maxsplit=1)[1]

    # Get completion from the LLM
    completion = get_completion(prompt_text)

    # Prepare the response message
    response_message = (
        f"Response: {completion['content']}\n\n"
        f"Prompt Tokens: {completion['prompt_tokens']}\n"
        f"Completion Tokens: {completion['completion_tokens']}\n"
        f"Total Tokens: {completion['total_tokens']}"
    )

    # Send the response back to the user
    await message.edit_text(f"Query: {prompt_text}\n{response_message}")


modules_help["midai"] = {"midai": "Ask a question to the LLM."}
