#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import random
import subprocess
from io import BytesIO

from pyrogram import Client, filters
from pyrogram.raw.functions.messages import SendMedia
from pyrogram.raw.types import DocumentAttributeAudio, InputMediaUploadedDocument
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.scripts import format_exc, import_library, generate_waveform

tabulate = import_library("tabulate")
edge_tts = import_library("edge_tts", "edge-tts")

from edge_tts import Communicate, list_voices
from edge_tts.constants import DEFAULT_VOICE
from tabulate import tabulate


async def send_voice(client, chat_id, voice_bytes, duration):
    waveform = generate_waveform(voice_bytes.getvalue())

    voice_bytes.seek(0)
    file = await client.save_file(voice_bytes)

    attr = DocumentAttributeAudio(duration=duration, voice=True, waveform=waveform)

    media = InputMediaUploadedDocument(
        file=file, mime_type="audio/ogg", attributes=[attr]
    )

    peer = await client.resolve_peer(chat_id)

    await client.invoke(
        SendMedia(
            peer=peer, media=media, message="", random_id=random.randint(1, 2**63)
        )
    )


async def get_duration(data: bytes):
    process = subprocess.run(
        ["mediainfo", "--Inform=Audio;%Duration%", "-"], input=data, capture_output=True
    )

    try:
        return int(process.stdout.decode().strip()) // 1000
    except:
        return 0


async def all_voices(*, proxy: str | None) -> None:
    """All available voices."""
    voices = await list_voices(proxy=proxy)
    voices = sorted(voices, key=lambda voice: voice["ShortName"])
    headers = ["Name", "Gender", "ContentCategories", "VoicePersonalities"]
    table = [
        [
            voice["ShortName"],
            voice["Gender"],
            ", ".join(voice["VoiceTag"]["ContentCategories"]),
            ", ".join(voice["VoiceTag"]["VoicePersonalities"]),
        ]
        for voice in voices
    ]
    return tabulate(table, headers)


@Client.on_message(filters.command("etts", prefix) & filters.me)
async def etts(client: Client, message: Message):
    if message.reply_to_message:
        lang = message.command[1]
        text = message.reply_to_message.text
    else:
        lang = message.command[1]
        text = " ".join(message.command[2:])

    await message.edit("<b>Speech synthesis...</b>")

    try:
        if lang == "all":
            voices = await all_voices(proxy=None)
            if len(voices) <= 4096:
                await message.edit(voices)
            else:
                with open("edge-voices.txt", "w") as f:
                    f.write(voices)
                await message.reply_document("edge-voices.txt")
                await message.delete()
                os.remove("edge-voices.txt")
            return

        if lang in ("d", "default"):
            lang = DEFAULT_VOICE

        if lang == "hi":
            lang = "hi-IN-SwaraNeural"

        if not text:
            await message.edit("<b>No text to speech</b>")
            return

        communicate = Communicate(text=text, voice=lang)
        communicate.save_sync("voice.ogg")

        with open("voice.ogg", "rb") as f:
            data = f.read()

        duration = await get_duration(data)

        voice = BytesIO(data)
        voice.name = "voice.ogg"

        await message.delete()
        await send_voice(client, message.chat.id, voice, duration)

        os.remove("voice.ogg")

    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("estts", prefix) & filters.me)
async def estts(client: Client, message: Message):
    if message.reply_to_message:
        lang = message.command[1]
        text = message.reply_to_message.text
    else:
        lang = message.command[1]
        text = " ".join(message.command[2:])

    await message.edit("<b>Speech synthesis...</b>")

    try:
        if lang == "all":
            voices = await all_voices(proxy=None)
            if len(voices) <= 4096:
                await message.edit(voices)
            else:
                with open("edge-voices.txt", "w") as f:
                    f.write(voices)
                await message.reply_document("edge-voices.txt")
                await message.delete()
                os.remove("edge-voices.txt")
            return

        if lang in ("d", "default"):
            lang = DEFAULT_VOICE

        if lang == "hi":
            lang = "hi-IN-SwaraNeural"

        if not text:
            await message.edit("<b>No text to speech</b>")
            return

        communicate = Communicate(text=text, voice=lang)
        submaker = edge_tts.SubMaker()

        with open("voice.ogg", "wb") as file:
            for chunk in communicate.stream_sync():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)

        with open("voice.srt", "w", encoding="utf-8") as file:
            file.write(submaker.get_srt())

        with open("voice.ogg", "rb") as f:
            data = f.read()

        duration = await get_duration(data)

        voice = BytesIO(data)
        voice.name = "voice.ogg"

        await message.delete()

        await send_voice(client, message.chat.id, voice, duration)
        await client.send_document(message.chat.id, "voice.srt")

        os.remove("voice.ogg")
        os.remove("voice.srt")

    except Exception as e:
        await message.edit(format_exc(e))


modules_help["edge-tts"] = {
    "etts [lang]* [text]*": "Say text",
    "etts [lang]* replied message": "Say text",
    "etts all": "Get all voices",
    "estts [lang]* [text]*": "Say text & Generate subtitles",
    "estts [lang]* replied message": "Say text & Generate subtitles"
    f"\n for default lang (en-US-EmmaMultilingualNeural) use 'd' or 'default' in lang place, for e.g., <code>{prefix}etts d hello</code>"
    f"\n\n<b>Example:</b>\n<code>{prefix}etts en-US-AriaNeural Hello world</code>",
}
