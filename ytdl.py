from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library
import os
from asyncio import get_event_loop


youtube_dl = import_library("youtube_dl")
pillow = import_library("PIL")
YoutubeDL = youtube_dl.YoutubeDL
DownloadError = youtube_dl.utils.DownloadError
ContentTooShortError = youtube_dl.utils.ContentTooShortError
ExtractorError = youtube_dl.utils.ExtractorError
GeoRestrictedError = youtube_dl.utils.GeoRestrictedError
MaxDownloadsReached = youtube_dl.utils.MaxDownloadsReached
PostProcessingError = youtube_dl.utils.PostProcessingError
UnavailableVideoError = youtube_dl.utils.UnavailableVideoError
XAttrMetadataError = youtube_dl.utils.XAttrMetadataError

strings = {
    "name": "Youtube-Dl",
    "preparing": "<b>[YouTube-Dl]</b> Preparing...",
    "downloading": "<b>[YouTube-Dl]</b> Downloading...",
    "working": "<b>[YouTube-Dl]</b> Working...",
    "exporting": "<b>[YouTube-Dl]</b> Exporting...",
    "reply": "<b>[YouTube-Dl]</b> No link!",
    "noargs": "<b>[YouTube-Dl]</b> No args!",
    "content_too_short": "<b>[YouTube-Dl]</b> Downloading content too short!",
    "geoban": "<b>[YouTube-Dl]</b> The video is not available for your geographical location due to geographical "
              "restrictions set by the website!",
    "maxdlserr": '<b>[YouTube-Dl]</b> The download limit is as follows: " oh ahah"',
    "pperr": "<b>[YouTube-Dl]</b> Error in post-processing!",
    "noformat": "<b>[YouTube-Dl]</b> Media is not available in the requested format",
    "xameerr": "<b>[YouTube-Dl]</b> {0.code}: {0.msg}\n{0.reason}",
    "exporterr": "<b>[YouTube-Dl]</b> Error when exporting video",
    "err": "<b>[YouTube-Dl]</b> {}"
}


rip_data = None


def download_video(opts, url):
    global rip_data
    try:
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except Exception as ex:
        rip_data = ex


@Client.on_message(filters.command(["ytdl", "yt", 'yt3', 'ytdl3'], prefix) & filters.me)
async def ytdl_handler(client: Client, message: Message):
    try:
        url = message.command[1]
    except IndexError:
        return await message.edit(strings["noargs"])
    await message.edit(strings["preparing"])
    if message.command[0] in ["yt3", "ytdl3"]:
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "downloads/%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        video = False
    else:
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "downloads/%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        video = True
    await message.edit(strings["downloading"])
    try:
        await get_event_loop().run_in_executor(None, lambda: download_video(opts, url))
        if type(rip_data) != dict:
            raise rip_data
    except DownloadError as DE:
        return await message.edit(strings["err"].format(DE))
    except ContentTooShortError:
        return await message.edit(strings["content_too_short"])
    except GeoRestrictedError:
        return await message.edit(strings["geoban"])
    except MaxDownloadsReached:
        return await message.edit(strings["maxdlserr"])
    except PostProcessingError:
        return await message.edit(strings["pperr"])
    except UnavailableVideoError:
        return await message.edit(strings["noformat"])
    except XAttrMetadataError as XAME:
        return await message.edit(strings["xameerr"].format(XAME))
    except ExtractorError:
        return await message.edit(strings["exporterr"])
    except Exception as e:
        return await message.edit('<b>[YouTube-Dl]</b>\n' + format_exc(e))

    if video:
        thumb = rip_data.get("thumbnail")
        if thumb:
            try:
                async with ClientSession() as session:
                    async with session.get(thumb) as resp:
                        if resp.status == 200:
                            with open('downloads/thumb.jpg', 'wb') as f_thumb:
                                f_thumb.write(await resp.read())
                                thumb = 'downloads/thumb.jpg'
                                im = pillow.Image.open(thumb)
                                im.convert('RGB').resize((im.size[0], 320), pillow.Image.ANTIALIAS).save(thumb, 'JPEG')
                        else:
                            thumb = None
            except:
                thumb = None
        await message.reply_video(f"downloads/{rip_data['id']}.mp4", caption=f'<b>{rip_data["title"]}</b>',
                                  thumb=thumb, duration=rip_data["duration"],
                                  width=rip_data["width"], height=rip_data["height"])
        os.remove(f"downloads/{rip_data['id']}.mp4")
        try:
            os.remove('downloads/thumb.jpg')
        except:
            pass
    else:
        await message.reply_audio(f"downloads/{rip_data['id']}.mp3", caption=f'<b>{rip_data["title"]}</b>',
                                  duration=rip_data["duration"])
        os.remove(f"downloads/{rip_data['id']}.mp3")

    return await message.delete()


modules_help['ytdl'] = {
    'yt [link]': 'Download video by link with best quality',
    'yt3 [link]': 'Download audio by link with best quality',
}
