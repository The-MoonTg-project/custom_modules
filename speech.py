import os
import requests
from asyncio import sleep
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

# Play.ht API Configuration
USER_ID = "uxynq8XNFuUIXG77byu3Vzq5Wm12"
API_KEY = "c30cb61772e643788fd963613685ae4a"
PLAY_HT_API_URL = "https://api.play.ht/api/v2/tts/stream"

# Average speaking rate (words per minute)
WORDS_PER_MINUTE = 150

# Define moods and their corresponding settings
MOODS = {
    "happy": {"rate": 170, "pitch": 1.1},
    "sad": {"rate": 130, "pitch": 0.9},
    "lazy": {"rate": 120, "pitch": 1.0},
    "tired": {"rate": 110, "pitch": 0.8},
    "normal": {"rate": 150, "pitch": 1.0},
}

@Client.on_message(filters.command("voice", prefix))
async def voice_command(client: Client, message: Message):
    """Generate a conversational voice with fake recording simulation."""
    if len(message.command) < 2:
        await message.reply("Usage: `voice <mood> <text>`")
        return

    # Extract mood and text from the command
    mood = "normal"  # Default mood
    if message.command[1] in MOODS:
        mood = message.command[1]
        text = " ".join(message.command[2:]).strip()
    else:
        text = " ".join(message.command[1:]).strip()

    # Delete the original command message
    await message.delete()

    # Start fake recording action
    recording_task = client.loop.create_task(fake_recording_action(client, message.chat.id, text))

    try:
        # Generate voice using Play.ht API with mood adjustments
        audio_path = await generate_conversational_audio(text, mood)
        if audio_path:
            # Wait until the fake recording action has completed before sending audio
            estimated_duration = estimate_audio_duration(text)
            await sleep(estimated_duration + 2)  # Adjust buffer time if needed
            # Send the generated voice message
            await client.send_voice(chat_id=message.chat.id, voice=audio_path)
            # Remove the audio file after sending
            os.remove(audio_path)
    except Exception as e:
        # Notify user of errors
        await client.send_message(message.chat.id, f"Error: {str(e)}")
    finally:
        # Ensure the fake recording action stops only after audio is sent
        recording_task.cancel()


async def fake_recording_action(client: Client, chat_id: int, text: str):
    """Simulate the 'recording voice' action until the audio is fully 'recorded'."""
    estimated_duration = estimate_audio_duration(text)  # Estimate the duration of the audio
    try:
        while estimated_duration > 0:
            await client.send_chat_action(chat_id=chat_id, action=enums.ChatAction.RECORD_AUDIO)
            await sleep(5)
            estimated_duration -= 5
    except Exception:
        pass


async def generate_conversational_audio(text: str, mood: str):
    """Generate audio using Play.ht API."""
    headers = {
        "X-USER-ID": USER_ID,
        "AUTHORIZATION": API_KEY,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }

    # Extract mood settings
    mood_settings = MOODS.get(mood, MOODS["normal"])

    payload = {
        "text": text,
        "voice_engine": "Play3.0",
        "voice": "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json",
        "output_format": "mp3",
        "rate": mood_settings["rate"],  # Adjust rate based on mood
        "pitch": mood_settings["pitch"],  # Adjust pitch based on mood
    }

    response = requests.post(PLAY_HT_API_URL, headers=headers, json=payload, timeout=15, stream=True)
    response.raise_for_status()

    # Save audio to file
    audio_path = "play_ht_conversational_voice.mp3"
    with open(audio_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return audio_path


def estimate_audio_duration(text: str) -> float:
    """Estimate the duration of the audio based on word count."""
    word_count = len(text.split())
    duration_in_seconds = (word_count / WORDS_PER_MINUTE) * 60
    return duration_in_seconds


# Module help
modules_help["voice"] = {
    "voice [mood] [text]": "Generate a conversational voice with mood variation and fake recording simulation. Moods: happy, sad, lazy, tired, normal.",
              }
