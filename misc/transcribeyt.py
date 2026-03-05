import asyncio
import os

import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from utils import modules_help, prefix

# Replace with your Gladia API key
gladia_key = "your key "
gladia_url = "https://api.gladia.io/v2/transcription/"


# Function to make fetch requests to the Gladia API
async def make_fetch_request(url, headers, method="GET", data=None):
    async with aiohttp.ClientSession() as session:
        if method == "POST":
            async with session.post(url, headers=headers, json=data) as resp:
                return await resp.json()
        else:
            async with session.get(url, headers=headers) as resp:
                return await resp.json()


@Client.on_message(filters.command("transcribeyt", prefix) & filters.me)
async def transcribe_audio(_, message: Message):
    """
    Transcribe an audio URL using the Gladia API.

    Usage: .transcribe <audio_url>
    """
    audio_url = (
        message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    )

    # Check if a valid URL was provided
    if not audio_url:
        await message.reply("Please provide a valid audio URL.")
        return

    headers = {"x-gladia-key": gladia_key, "Content-Type": "application/json"}

    request_data = {"audio_url": audio_url}

    # Send initial request to Gladia API
    status_message = await message.reply("- Sending initial request to Gladia API...")
    initial_response = await make_fetch_request(
        gladia_url, headers, "POST", request_data
    )

    # Check if the response contains the result_url
    if "result_url" not in initial_response:
        await status_message.edit(f"Error in transcription request: {initial_response}")
        return

    result_url = initial_response["result_url"]
    await status_message.edit(
        f"Initial request sent. Polling for transcription results..."
    )

    # Polling for transcription result
    while True:
        poll_response = await make_fetch_request(result_url, headers)

        if poll_response.get("status") == "done":
            transcription = (
                poll_response.get("result", {})
                .get("transcription", {})
                .get("full_transcript")
            )
            if transcription:
                # Format the transcription result with HTML
                result_html = f"""
                <u><b>Transcription Result</b></u>
                <br>
                <pre>{transcription}</pre>
                """
                try:
                    # Attempt to send transcription as a message
                    await message.reply_text(
                        result_html, parse_mode=enums.ParseMode.HTML
                    )
                except MessageTooLong:
                    # Save the large response to a file
                    with open("transcription.txt", "w") as f:
                        f.write(result_html)

                    # Read general details to include in the caption
                    general_details = "Here's the transcription result."

                    # Send the file with a caption
                    await message.reply_document(
                        "transcription.txt",
                        caption=f"<u><b>General Details</b></u>:\n{general_details}",
                    )

                    # Clean up by removing the file
                    os.remove("transcription.txt")
            else:
                await status_message.edit(
                    "Transcription completed, but no transcript was found."
                )
            break
        else:
            await status_message.edit(
                f"Transcription status: {poll_response.get('status')}"
            )
            await asyncio.sleep(30)  # Wait for a few seconds before polling again


modules_help["transcribeyt"] = {
    "transcribeyt [yt video url]": "Reply with a YT video link to get transcribed "
}
