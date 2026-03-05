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

from pyrogram import Client, enums, filters
from pyrogram.raw.functions.messages import SendMedia
from pyrogram.raw.types import (
    DocumentAttributeAudio,
    InputMediaUploadedDocument,
)
from pyrogram.types import Message
from utils.scripts import format_exc, generate_waveform, import_library

from utils import modules_help, prefix

gTTS = import_library("gtts").gTTS

@Client.on_message(filters.command("tts", prefix) & filters.me)
async def tts(client: Client, message: Message):
    if message.reply_to_message:
        lang = message.command[1]
        text = message.reply_to_message.text
    else:
        lang = message.command[1]
        text = " ".join(message.command[2:])

    await message.edit("<b>Speech synthesis...</b>", parse_mode=enums.ParseMode.HTML)

    try:
        tts = gTTS(text, lang=lang)
        tts.save("voice.ogg")

        with open("voice.ogg", "rb") as f:
            data = f.read()

        voice = BytesIO(data)
        voice.name = "voice.ogg"
        waveform = generate_waveform(data)

        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            "voice.ogg"
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)

        try:
            audio_duration = int(float(process.stdout.strip()))
        except (ValueError, TypeError):
            audio_duration = 0

        file = await client.save_file(voice)

        attr = DocumentAttributeAudio(
            duration=audio_duration, voice=True, waveform=waveform
        )

        media = InputMediaUploadedDocument(
            file=file, mime_type="audio/ogg", attributes=[attr]
        )

        peer = await client.resolve_peer(message.chat.id)

        await message.delete()

        await client.invoke(
            SendMedia(
                peer=peer, media=media, message="", random_id=random.randint(1, 2**63)
            )
        )

    except Exception as e:
        await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)

    finally:
        if os.path.exists("voice.ogg"):
            os.remove("voice.ogg")


modules_help["tts"] = {
    "tts [lang]* [text]*": "Say text",
    "tts [lang]* replied message": "Say text",
}
