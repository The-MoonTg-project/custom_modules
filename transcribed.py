
import requests
import time
from pyrogram import Client, filters
from pyrogram import Client, filters, enums
from pyrogram.errors import MessageTooLong
import os
import time
from utils.misc import modules_help, prefix


# Replace with your Gladia API key
gladia_key = "youe key 🗝️"
gladia_url = "https://api.gladia.io/v2/transcription/"

# Function to make fetch requests to the Gladia API
def make_fetch_request(url, headers, method='GET', data=None):
    if method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    else:
        response = requests.get(url, headers=headers)
    return response.json()




@Client.on_message(filters.command("transcribe", prefix) & filters.me)
async def transcribe_audio(client, message):
    audio_url = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    # Check if a valid URL was provided
    if not audio_url:
        await message.reply("Please provide a valid audio URL.")
        return

    headers = {
        "x-gladia-key": gladia_key,
        "Content-Type": "application/json"
    }

    request_data = {"audio_url": audio_url}

    # Send initial request to Gladia API
    await message.reply("- Sending initial request to Gladia API...")
    initial_response = make_fetch_request(gladia_url, headers, 'POST', request_data)

    # Check if the response contains the result_url
    if 'result_url' not in initial_response:
        await message.reply(f"Error in transcription request: {initial_response}")
        return

    result_url = initial_response["result_url"]
    await message.edit(f"Initial request sent. Polling for transcription results...")

    # Polling for transcription result
    while True:
        poll_response = make_fetch_request(result_url, headers)

        if poll_response.get("status") == "done":
            transcription = poll_response.get("result", {}).get("transcription", {}).get("full_transcript")
            if transcription:
                info = f"- Transcription done: \n\n{transcription}"

                try:
                    # Attempt to send transcription as a message
                    await message.reply_text(info, parse_mode=enums.ParseMode.MARKDOWN)
                except MessageTooLong:
                    # Save the large response to a file
                    with open("transcription.txt", "w") as f:
                        f.write(info)

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
                await message.edit("Transcription completed, but no transcript was found.")
            break
        else:
            await message.edit(f"Transcription status: {poll_response.get('status')}")
            time.sleep(30)  # Wait for a few seconds before polling again


modules_help["transcribe"] = {
    "transcribe [yt video url]": " reply with yt video link to  getting transcribed "
     
}
