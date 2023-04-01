import os
import logging
import os
import pathlib
import shutil
import time
import shlex
import math
import uuid
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library

from fsplit.filesplit import Filesplit

async def edit_or_reply(message, text, parse_mode="md"):
    if not message:
        return await message.edit(text, parse_mode=parse_mode)
    if not message.from_user:
        return await message.edit(text, parse_mode=parse_mode)
    if message.from_user.id in sudo_lis_t:
        if message.reply_to_message:
            return await message.reply_to_message.reply_text(text, parse_mode=parse_mode)
        return await message.reply_text(text, parse_mode=parse_mode)
    return await message.edit(text, parse_mode=parse_mode)

async def progress(current, total, message, start, type_of_ps, file_name=None):
    """Progress Bar For Showing Progress While Uploading / Downloading File - Normal"""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        if elapsed_time == 0:
            return
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "{0}{1} {2}%\n".format(
            "".join(["▰" for i in range(math.floor(percentage / 10))]),
            "".join(["▱" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(total), time_formatter(estimated_total_time)
        )
        if file_name:
            try:
                await message.edit(
                    "{}\n**File Name:** `{}`\n{}".format(type_of_ps, file_name, tmp)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass
        else:
            try:
                await message.edit("{}\n{}".format(type_of_ps, tmp))
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass

def humanbytes(size):
    """Convert Bytes To Bytes So That Human Can Read It"""
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"

def get_text(message: Message) -> [None, str]:
    """Extract Text From Commands"""
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None

@Client.on_message(filters.command(["setthumb"], prefix) & filters.me)
async def st(client, message):
    engine = message.Engine
    pablo = await edit_or_reply(message, engine.get_string("PROCESSING"))
    if not message.reply_to_message:
        await pablo.edit(engine.get_string("FILE_TOOLS_6"))
        return
    if not message.reply_to_message.photo:
        await pablo.edit(engine.get_string("FILE_TOOLS_6"))
        return
    await message.reply_to_message.download(file_name="./main_startup/Cache/thumb.jpg")
    await pablo.edit(
        engine.get_string("FILE_TOOLS_7")
    )


image_ext = tuple([".jpg", ".png", ".jpeg"])
vid_ext = tuple([".mp4", ".mkv"])
sticker_ext = tuple([".wepb", ".tgs"])
song_ext = tuple([".mp3", ".wav", ".m4a"])

@Client.on_message(filters.command(["upl"], prefix) & filters.me)
async def upload(client: Client, message: Message):
    engine = message.Engine
    pablo = await edit_or_reply(message, engine.get_string("PROCESSING"))
    file = get_text(message)
    c_time = time.time()
    if not file:
        await pablo.edit(
            engine.get_string("INPUT_REQ").format("File Path")
            )
        return
    if not os.path.exists(file):
        await pablo.edit(engine.get_string("F_404"))
        return
    file_name = os.path.basename(file)
    send_as_thumb = bool(os.path.exists("./main_startup/Cache/thumb.jpg"))
    size = os.stat(file).st_size
    if file.endswith(image_ext):
        # assume its image file
        capt = f"File Name : `{file_name}` \nFile Size : `{humanbytes(size)}` \nFile Type : `Image (Guessed)`"
        await client.send_photo(
            message.chat.id,
            file,
            caption=capt,
            progress=progress,
            progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
        )
    elif file.endswith(vid_ext):
        capt = f"File Name : `{file_name}` \nFile Size : `{humanbytes(size)}` \nFile Type : `Video (Guessed)`"
        if send_as_thumb:
            await client.send_video(
                message.chat.id,
                file,
                thumb="./main_startup/Cache/thumb.jpg",
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
        else:
            await client.send_video(
                message.chat.id,
                file,
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
    elif file.endswith(".gif"):
        capt = f"File Name : `{file_name}` \nFile Size : `{humanbytes(size)}` \nFile Type : `Gif (Guessed)`"
        if send_as_thumb:
            await client.send_animation(
                message.chat.id,
                file,
                thumb="./main_startup/Cache/thumb.jpg",
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
        else:
            await client.send_animation(
                message.chat.id,
                file,
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
    elif file.endswith(song_ext):
        capt = f"File Name : `{file_name}` \nFile Size : `{humanbytes(size)}` \nFile Type : `Audio (Guessed)`"
        if send_as_thumb:
            await client.send_audio(
                message.chat.id,
                file,
                thumb="./main_startup/Cache/thumb.jpg",
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
        else:
            await client.send_audio(
                message.chat.id,
                file,
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
    elif file.endswith(sticker_ext):
        await client.send_sticker(
            message.chat.id,
            file,
            progress=progress,
            progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
        )
    else:
        capt = f"File Name : `{file_name}` \nFile Size : `{humanbytes(size)}` \nFile Type : `Document (Guessed)`"
        if send_as_thumb:
            await client.send_document(
                message.chat.id,
                file,
                thumb="./main_startup/Cache/thumb.jpg",
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
        else:
            await client.send_document(
                message.chat.id,
                file,
                caption=capt,
                progress=progress,
                progress_args=(pablo, c_time, f"`Uploading {file_name}!`", file_name),
            )
    await pablo.delete()

