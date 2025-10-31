import os
import requests
from urllib.parse import quote
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

API_URL = "https://api.deline.web.id/tools/whatmusic?url="

@Client.on_message(filters.command("shazam", prefix))
async def shazam_music(client, message: Message):
    reply = message.reply_to_message
    if not (reply and (reply.audio or reply.voice)):
        return await message.edit("Reply to an audio or voice message to identify the music.")

    await message.edit("Processing audio...")
    audio_path = await client.download_media(reply.audio or reply.voice)

    try:
        with open(audio_path, "rb") as f:
            upload = requests.post("https://x0.at", files={"file": f})
            upload.raise_for_status()
            audio_url = upload.text.strip()

        res = requests.get(f"{API_URL}{quote(audio_url)}").json()
        if res.get("status") and "result" in res:
            result = res["result"]
            title = result.get("title", "Unknown")
            artist = result.get("artists", "Unknown")
            await message.edit(
                f"**Music Identified**\n\n**Title:** {title}\n**Artist:** {artist}",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        else:
            await message.edit("Couldn’t identify the music. Try again with clearer audio.")
    except Exception as e:
        await message.edit(f"Error: {e}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

modules_help["shazam"] = {
    "shazam": "Reply to an audio or voice file to identify the music.",
}
