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

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library

tabulate = import_library("tabulate")
edge_tts = import_library("edge_tts", "edge-tts")

from tabulate import tabulate

from edge_tts import Communicate, list_voices
from edge_tts.constants import DEFAULT_VOICE


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
        if lang == "d" or lang == "default":
            lang = DEFAULT_VOICE
        if not text:
            await message.edit("<b>No text to speech</b>")
            return
        communicate = Communicate(text=text, voice=lang)
        communicate.save_sync("voice.ogg")

        await message.delete()
        if message.reply_to_message:
            await message.reply_to_message.reply_audio("voice.ogg")
        else:
            await client.send_audio(message.chat.id, "voice.ogg")
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
        if lang == "d" or lang == "default":
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

        await message.delete()
        if message.reply_to_message:
            await message.reply_to_message.reply_audio("voice.ogg")
            await message.reply_to_message.reply_document("voice.srt")
        else:
            await client.send_audio(message.chat.id, "voice.ogg")
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
