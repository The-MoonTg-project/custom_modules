import asyncio
import os
from contextlib import suppress
from subprocess import PIPE

import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library, with_reply, restart

pytgcalls = import_library("pytgcalls","pytgcalls==3.0.0.dev24")
yt_dlp = import_library("yt_dlp")
from pytgcalls import GroupCallFactory

group_call = None


def init_client(func):
    async def wrapper(client, message):
        global group_call
        if not group_call:
            group_call = GroupCallFactory(client).get_file_group_call()
            group_call.enable_logs_to_console = False

        return await func(client, message)

    return wrapper


@Client.on_message(filters.command("play", prefix) & filters.me)
@with_reply
async def start_playout(_, message: Message):
    if not group_call:
        await message.reply(
            f"<b>You are not joined [type <code>{prefix}join</code>]</b>"
        )
        return
    if not message.reply_to_message.audio:
        await message.edit("<b>Reply to a message containing audio</b>")
        return
    input_filename = "input.raw"
    await message.edit("<b>Downloading...</b>")
    audio_original = await message.reply_to_message.download()
    await message.edit("<b>Converting..</b>")
    ffmpeg.input(audio_original).output(
        input_filename, format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(audio_original)
    await message.edit(f"<b>Playing {message.reply_to_message.audio.title}</b>...")
    group_call.input_filename = input_filename

@Client.on_message(filters.command("yplay", prefix) & filters.me)
async def start_ytplayout(_, message: Message):
    if not group_call:
        await message.reply(
            f"<b>You are not joined [type <code>{prefix}join</code>]</b>"
        )
        return
    if len(message.command) > 1:
      yt_link = message.text.split(maxsplit=1)[1]
    input_filename = "input.raw"
    await message.edit_text("<b>Downloading...</b>")
    # audio_original = await message.reply_to_message.download()
    # await message.edit("<b>Converting..</b>")
    if yt_link.startswith("https://"):
        try:
            yt = await asyncio.create_subprocess_shell(
                f'ffmpeg -i "$(yt-dlp -x -g "{yt_link}")" -f s16le -ac 2 -ar 48000 -acodec pcm_s16le {input_filename}',
                stdout=PIPE,
                stderr=PIPE,
            )
            if yt.returncode !=0:
                await asyncio.sleep(30)
                await message.edit_text(f"<b>Playing</b>...")
                group_call.input_filename = input_filename
        except Exception as e:
            await message.edit_text(format_exc(e))
    else:
        try:
            yt = await asyncio.create_subprocess_shell(
                f'ffmpeg -i "$(yt-dlp -x -g --default-search "ytsearch" "{yt_link}")" -f s16le -ac 2 -ar 48000 -acodec pcm_s16le {input_filename}',
                stdout=PIPE,
                stderr=PIPE,
            )
            if yt.returncode !=0:
                await asyncio.sleep(30)
                await message.edit_text(f"<b>Playing</b>...")
                group_call.input_filename = input_filename
        except Exception as e:
            await message.edit_text(format_exc(e))

@Client.on_message(filters.command("volume", prefix) & filters.me)
@init_client
async def volume(_, message):
    if len(message.command) < 2:
        await message.edit("<b>You forgot to pass volume [1-200]</b>")
    await group_call.set_my_volume(message.command[1])
    await message.edit(
        f"<b>Your volume is set to</b><code> {message.command[1]}</code>"
    )


@Client.on_message(filters.command("join", prefix) & filters.me)
@init_client
async def start(_, message: Message):
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    with suppress(ValueError):
        chat_id = int(chat_id)

    try:
        await group_call.start(chat_id)
        await message.edit("<b>Joined VC successfully!</b>")
    except Exception as e:
        await message.edit(f"<b>An unexpected error has occurred: <code>{e}</code></b>")


@Client.on_message(filters.command("leave_vc", prefix) & filters.me)
@init_client
async def stop(_, message: Message):
    try:
        # os.remove('input.raw')
        await group_call.stop()
        await message.edit("<b>Leaving successfully!</b>")
    except Exception as e:
        await message.edit(
            f"<b>Аn unexpected error occurred [<code>{e}</code>]\n"
            "The bot will try to exit the voice chat by restarting itself,"
            "the bot will be unavailable for the next 4 seconds</b>"
        )
        restart()


@Client.on_message(filters.command("stop", prefix) & filters.me)
@init_client
async def stop_playout(_, message: Message):
    group_call.stop_playout()
    os.remove('input.raw')
    await message.edit("<b>Stopped successfully!</b>")


@Client.on_message(filters.command("vmute", prefix) & filters.me)
@init_client
async def mute(_, message: Message):
    group_call.set_is_mute(True)
    await message.edit("<b>Sound off!</b>")


@Client.on_message(filters.command("vunmute", prefix) & filters.me)
@init_client
async def unmute(_, message: Message):
    group_call.set_is_mute(False)
    await message.edit("<b>Sound on!</b>")


@Client.on_message(filters.command("pause", prefix) & filters.me)
@init_client
async def pause(_, message: Message):
    group_call.pause_playout()
    await message.edit("<b>Paused!</b>")


@Client.on_message(filters.command("resume", prefix) & filters.me)
@init_client
async def resume(_, message: Message):
    group_call.resume_playout()
    await message.edit("<b>Resumed!</b>")


modules_help["voice_chat"] = {
    "play [reply]*": "Play audio in replied message",
    "yplay [link/search term]*": "Play audio from given link[preferred youtube]",
    "volume [1 – 200]": "Set the volume level from 1 to 200",
    "join [chat_id]": "Join the voice chat",
    "leave_vc": "Leave voice chat",
    "stop": "Stop playback",
    "vmute": "Mute the userbot",
    "vunmute": "Unmute the userbot",
    "pause": "Pause",
    "resume": "Resume",
}
