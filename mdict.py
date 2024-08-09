import aiohttp
from io import BytesIO
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

MERRIAM_WEBSTER_API_KEY = "2b7f5901-40e0-4007-9c06-4d38218a62ab"
AUDIO_BASE_URL = "https://media.merriam-webster.com/soundc11"

async def merriam_webster_search(word):
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={MERRIAM_WEBSTER_API_KEY}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

async def format_definition(word, search_results):
    result_text = f"**Definition of {word.capitalize()}:**\n\n"
    audio_files = []

    if isinstance(search_results[0], dict):
        for entry in search_results:
            result_text += f"**Word:** {entry.get('meta', {}).get('id', 'N/A')}\n"
            if 'shortdef' in entry:
                result_text += "**Definitions:**\n"
                for i, definition in enumerate(entry['shortdef']):
                    result_text += f"    {i + 1}. {definition}\n"
            result_text += f"**Part of Speech:** {entry.get('fl', 'N/A')}\n"
            if 'hwi' in entry and 'prs' in entry['hwi']:
                for pron in entry['hwi']['prs']:
                    result_text += f"**Pronunciation:** {pron.get('mw', 'N/A')}\n"
                    if 'sound' in pron:
                        audio_file = pron['sound']['audio']
                        subdir = audio_file[0]
                        audio_url = f"{AUDIO_BASE_URL}/{subdir}/{audio_file}.wav"
                        audio_files.append(audio_url)
            result_text += "\n"
    else:
        result_text += "No definitions found.\n"

    return result_text, audio_files

@Client.on_message(filters.command(["explain", "exp"], prefix) & filters.me)
async def merriam_webster_command(client, message: Message):
    try:
        word = message.reply_to_message.text.strip() if message.reply_to_message else None
        if not word:
            command_parts = message.text.split(' ', 1)
            if len(command_parts) < 2:
                await message.edit_text("Please provide a word to define.")
                return
            word = command_parts[1].strip()

        search_results = await merriam_webster_search(word)

        if not search_results:
            await message.edit_text("No results found.")
            return

        result_text, audio_files = await format_definition(word, search_results)
        
        max_caption_length = 2000
        parts = [result_text[i:i + max_caption_length] for i in range(0, len(result_text), max_caption_length)]

        await message.edit_text(parts[0], parse_mode=enums.ParseMode.MARKDOWN)
        for part in parts[1:]:
            await message.reply_text(part, parse_mode=enums.ParseMode.MARKDOWN)

        for audio_url in audio_files:
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url) as audio_response:
                    if audio_response.status == 200:
                        audio_data = await audio_response.read()
                        audio_stream = BytesIO(audio_data)
                        audio_stream.name = f"{word}.wav"
                        await message.reply_audio(audio=audio_stream, title=f"Pronunciation of {word}")

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")

@Client.on_message(filters.command(["define", "def"], prefix) & filters.me)
async def short_definition_command(client, message: Message):
    try:
        word = message.reply_to_message.text.strip() if message.reply_to_message else None
        if not word:
            command_parts = message.text.split(' ', 1)
            if len(command_parts) < 2:
                await message.edit_text("Please provide a word to define.")
                return
            word = command_parts[1].strip()

        search_results = await merriam_webster_search(word)

        if not search_results:
            await message.edit_text("No results found.")
            return

        short_definitions = f"**– Short Definitions of {word.capitalize()}:**\n\n"
        if isinstance(search_results[0], dict):
            for entry in search_results:
                if 'shortdef' in entry:
                    for i, definition in enumerate(entry['shortdef']):
                        short_definitions += f"    {i + 1}. {definition}\n"
        else:
            short_definitions = "No definitions found.\n"

        max_caption_length = 1024
        parts = [short_definitions[i:i + max_caption_length] for i in range(0, len(short_definitions), max_caption_length)]

        await message.edit_text(parts[0], parse_mode=enums.ParseMode.MARKDOWN)
        for part in parts[1:]:
            await message.reply_text(part, parse_mode=enums.ParseMode.MARKDOWN)

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")

modules_help["dictionary"] = {
    "explain [word]": "Detailed information of word",
    "exp [word]": "Detailed information of word",
    "define [word]": "Short information of word",
    "def [word]": "Short information of word",
              }
