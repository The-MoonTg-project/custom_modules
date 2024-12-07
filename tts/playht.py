import os
from asyncio import sleep

from pyrogram import Client, filters, enums
from pyrogram.types import Message


from utils.misc import modules_help, prefix
from utils.scripts import import_library
from utils.db import db

import_library("pyht")

from pyht import Client as PlayHTClient
from pyht.client import TTSOptions

# Default Play.ht configuration
DEFAULT_PARAMS = {
    "voice": "s3://voice-cloning-zero-shot/ec7103a2-a80c-46a1-b8dd-fca1179e2b5d/original/manifest.json",
    "speed": 1.0,
    "temperature": 1.0,
    "sample_rate": 22050,
    "seed": 42,
    "voice_guidance": 4.0,
    "style_guidance": 10.0,
    "text_guidance": 1.5,
}


# Get Play.ht client
def get_playht_client():
    user_id = db.get("custom.playht", "user_id")
    api_key = db.get("custom.playht", "api_key")
    if not user_id or not api_key:
        raise ValueError(
            f"Play.ht `user_id` or `api_key` is not configured. Use `{prefix}set_playht` to set them."
        )
    return PlayHTClient(user_id=user_id, api_key=api_key)


# Estimate audio duration
def estimate_audio_duration(text: str) -> float:
    words_per_minute = 150
    return len(text.split()) / words_per_minute * 60


# Generate Play.ht audio
async def generate_conversational_audio(text: str):
    params = {
        key: db.get("custom.playht", key, default)
        for key, default in DEFAULT_PARAMS.items()
    }
    options = TTSOptions(
        voice=params["voice"],
        speed=float(params["speed"]),
        temperature=float(params["temperature"]),
        sample_rate=int(params["sample_rate"]),
        seed=int(params["seed"]),
        voice_guidance=float(params["voice_guidance"]),
        style_guidance=float(params["style_guidance"]),
        text_guidance=float(params["text_guidance"]),
    )
    client = get_playht_client()
    audio_path = "play_ht_conversational_voice.mp3"

    with open(audio_path, "wb") as f:
        for chunk in client.tts(text, options):
            f.write(chunk)
    client.close()

    return audio_path


# Simulate recording action
async def fake_recording_action(client: Client, chat_id: int, text: str):
    duration = estimate_audio_duration(text)
    try:
        while duration > 0:
            await client.send_chat_action(chat_id, enums.ChatAction.RECORD_AUDIO)
            await sleep(5)
            duration -= 5
    except Exception:
        pass


# Command: Play.ht voice generation
@Client.on_message(filters.command("playht", prefix))
async def voice_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(
            "❌ **Usage:**\n"
            f"`{prefix}playht <text>`\n\n"
            "Generate a conversational voice message from the given text. Example:\n"
            f"`{prefix}playht Hello, how are you?`",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return

    text = " ".join(message.command[1:]).strip()
    await message.delete()

    recording_task = client.loop.create_task(
        fake_recording_action(client, message.chat.id, text)
    )
    try:
        audio_path = await generate_conversational_audio(text)
        if audio_path:
            await sleep(estimate_audio_duration(text) + 2)
            await client.send_voice(chat_id=message.chat.id, voice=audio_path)
            os.remove(audio_path)
    except Exception as e:
        await client.send_message("me", f"Error: {e}")
    finally:
        recording_task.cancel()


# Command: Set or view Play.ht configuration
@Client.on_message(filters.command("set_playht", prefix) & filters.me)
async def set_playht_config(_, message: Message):
    args = message.command
    if len(args) == 1:
        current_values = {
            key: db.get("custom.playht", key, default)
            for key, default in DEFAULT_PARAMS.items()
        }
        user_id = db.get("custom.playht", "user_id", "Not Set")
        api_key = db.get("custom.playht", "api_key", "Not Set")
        response = (
            "💡 **Current Play.ht Configuration:**\n"
            f"- **user_id**: `{user_id}`\n"
            f"- **api_key**: `{api_key}`\n"
            + "\n".join(
                [f"- **{key}**: `{value}`" for key, value in current_values.items()]
            )
            + "\n\n**Usage:**\n"
            f"`{prefix}set_playht <key> <value>`\n"
            "**Keys:** `user_id`, `api_key`, `voice`, `speed`, `temperature`, "
            "`sample_rate`, `seed`, `voice_guidance`, `style_guidance`, `text_guidance`"
        )
        await message.edit_text(response, parse_mode=enums.ParseMode.MARKDOWN)
        return

    if len(args) < 3:
        await message.edit_text(
            "❌ **Invalid Usage:**\n"
            f"`{prefix}set_playht <key> <value>`\n"
            f"Use `{prefix}set_playht` without arguments to see the current configuration.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return

    key = args[1].lower()
    value = " ".join(args[2:])
    if key not in ["user_id", "api_key", *DEFAULT_PARAMS.keys()]:
        await message.edit_text(
            "❌ **Invalid Key:**\n"
            "Allowed keys are: `user_id`, `api_key`, `voice`, `speed`, `temperature`, "
            "`sample_rate`, `seed`, `voice_guidance`, `style_guidance`, `text_guidance`.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return

    # Convert to appropriate types
    if key in [
        "speed",
        "temperature",
        "voice_guidance",
        "style_guidance",
        "text_guidance",
    ]:
        try:
            value = float(value)
        except ValueError:
            await message.edit_text(
                f"❌ `{key}` must be a numeric value (float).",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
            return
    elif key in ["sample_rate", "seed"]:
        try:
            value = int(value)
        except ValueError:
            await message.edit_text(
                f"❌ `{key}` must be an integer value.",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
            return

    db.set("custom.playht", key, value)
    await message.edit_text(
        f"✅ **Play.ht {key} updated successfully!**\nNew value: `{value}`",
        parse_mode=enums.ParseMode.MARKDOWN,
    )


# Module help
modules_help["playht"] = {
    "playht [text]*": "Generate a conversational voice with fake recording simulation.",
    "set_playht": "View or update Play.ht configuration parameters."
    f"\nFormat: {prefix}set_playht <key> <value> - Set a specific Play.ht parameter.",
}
