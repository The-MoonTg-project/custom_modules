from aiohttp import ClientSession
import asyncio
import os
import time
import requests
from utils.scripts import format_exc, import_library
wget = import_library("wget")
import wget
youtube_dl = import_library("youtube_dl")
from youtube_dl import YoutubeDL
from youtubesearchpython import SearchVideos
import threading
from concurrent.futures import ThreadPoolExecutor
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix


async def edit_or_reply(message, text, parse_mode="md"):
    sudo_lis_t = await sudo_list()
    """Edit Message If Its From Self, Else Reply To Message, (Only Works For Sudo's)"""
    if not message:
        return await message.edit(text, parse_mode=parse_mode)
    if not message.from_user:
        return await message.edit(text, parse_mode=parse_mode)
    if message.from_user.id in sudo_lis_t:
        if message.reply_to_message:
            return await message.reply_to_message.reply_text(text, parse_mode=parse_mode)
        return await message.reply_text(text, parse_mode=parse_mode)
    return await message.edit(text, parse_mode=parse_mode)

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

def run_in_exc(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(exc_, lambda: f(*args, **kwargs))
    return wrapper


def time_formatter(milliseconds: int) -> str:
    """Time Formatter"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " day(s), ") if days else "")
        + ((str(hours) + " hour(s), ") if hours else "")
        + ((str(minutes) + " minute(s), ") if minutes else "")
        + ((str(seconds) + " second(s), ") if seconds else "")
        + ((str(milliseconds) + " millisecond(s), ") if milliseconds else "")
    )
    return tmp[:-2]

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

async def _dl(url, file_name=None):
    if not file_name:
        from urllib.parse import urlparse
        a = urlparse(url)
        file_name = os.path.basename(a.path)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            f = await aiofiles.open(file_name, mode="wb")
            await f.write(await resp.read())
            await f.close()
    return file_name

def edit_msg(client, message, to_edit):
    try:
        client.loop.create_task(message.edit(to_edit))
    except MessageNotModified:
        pass
    except FloodWait as e:
        client.loop.create_task(asyncio.sleep(e.x))
    except TypeError:
        pass
    
def download_progress_hook(d, message, client):
    if d['status'] == 'downloading':
        current = d.get("_downloaded_bytes_str") or humanbytes(int(d.get("downloaded_bytes", 1)))
        total = d.get("_total_bytes_str") or d.get("_total_bytes_estimate_str")
        file_name = d.get("filename")
        eta = d.get('_eta_str', "N/A")
        percent = d.get("_percent_str", "N/A")
        speed = d.get("_speed_str", "N/A")
        to_edit = f"<b><u>Downloading File</b></u> \n<b>File Name :</b> <code>{file_name}</code> \n<b>File Size :</b> <code>{total}</code> \n<b>Speed :</b> <code>{speed}</code> \n<b>ETA :</b> <code>{eta}</code> \n<i>Download {current} out of {total}</i> (__{percent}__)"
        threading.Thread(target=edit_msg, args=(client, message, to_edit)).start()

@run_in_exc
def yt_dl(url, client, message, type_):
    if type_ == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "progress_hooks": [lambda d: download_progress_hook(d, message, client)],
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
    else:
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "progress_hooks": [lambda d: download_progress_hook(d, message, client)],
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
    with YoutubeDL(opts) as ytdl:
        ytdl_data = ytdl.extract_info(url, download=True)
    file_name = f"{ytdl_data['id']}.mp3" if type_ == "audio" else f"{ytdl_data['id']}.mp4"
    print(file_name)
    return file_name, ytdl_data


@Client.on_message(filters.command("yt","ytdl", prefix) & filters.me)
async def yt_vid(client, message):
    input_str = get_text(message)
    engine = message.Engine
    type_ = "video"
    pablo = await edit_or_reply(message, engine.get_string("PROCESSING"))
    if not input_str:
        await pablo.edit(
            engine.get_string("INPUT_REQ").format("Query")
        )
        return
    _m = ('http://', 'https://')
    if "|" in input_str:
        input_str = input_str.strip()
        input_str, type_ = input_str.split("|")
    if type_ not in ['audio', 'video']:
        return await pablo.edit(engine.get_string("NEEDS_C_INPUT"))
    if input_str.startswith(_m):
        url = input_str
    else:
        await pablo.edit(engine.get_string("GETTING_RESULTS").format(input_str))
        search = SearchVideos(str(input_str), offset=1, mode="dict", max_results=1)
        if not search:
            return await pablo.edit(engine.get_string("NO_RESULTS").format(input_str))
        rt = search.result()
        result_s = rt["search_result"]
        url = result_s[0]["link"]
    try:
        yt_file, yt_data = await yt_dl(url, client, message, type_)
    except Exception as e:
        return await pablo.edit(engine.get_string("YTDL_FAILED").format(e))
    vid_title = yt_data['title']
    uploade_r = yt_data['uploader']
    yt_id = yt_data['id']
    msg = message.reply_to_message or message 
    thumb_url = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
    thumb = await _dl(thumb_url)
    caption = f"**{type_.title()} Name ➠** `{vid_title}` \n**Requested For ➠** `{input_str}` \n**Channel ➠** `{uploade_r}` \n**Link ➠** `{url}`"
    c_time = time.time()
    if type_ == "video":
        await msg.reply_video(
            yt_file,
            duration=int(yt_data["duration"]),
            thumb=thumb,
            caption=caption,
            supports_streaming=True,
            progress=progress,
            progress_args=(
                pablo,
                c_time,
                f"`Uploading Downloaded Youtube File.`",
                str(yt_file),
            ),
        )
    else:
        await msg.reply_audio(
            yt_file,
            duration=int(yt_data["duration"]),
            title=str(yt_data["title"]),
            performer=uploade_r,
            thumb=thumb,
            caption=caption,
            progress=progress,
            progress_args=(
                pablo,
                c_time,
                f"`Uploading Downloaded Youtube File.`",
                str(yt_file),
            ),
        )
    await pablo.delete()
    for files in (thumb, yt_file):
        if files and os.path.exists(files):
            os.remove(files)
modules_help['ytdl'] = {
    'yt [link]': 'Download video by link with best quality',
    'yt3 [link]': 'Download audio by link with best quality',
}
