import asyncio
import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pyrogram import Client, filters
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix

# noinspection PyUnresolvedReferences
from utils.scripts import import_library, format_exc


VideoFileClip = import_library("moviepy.editor", "moviepy").VideoFileClip

im = None


def process_img(filename):
    global im
    im = Image.open(f"downloads/{filename}")
    w, h = im.size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(im, (0, 0))
    m = min(w, h)
    img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((10, 10, w - 10, h - 10), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    img = ImageOps.fit(img, (w, h))
    img.putalpha(mask)
    im = BytesIO()
    im.name = "img.webp"
    img.save(im)
    im.seek(0)


video = None


def process_vid(filename):
    global video
    video = VideoFileClip(f"downloads/{filename}")
    video.reader.close()
    w, h = video.size
    m = min(w, h)
    box = [(w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2]
    video = video.crop(*box)


@Client.on_message(filters.command(["circle", "round"], prefix) & filters.me)
async def circle(client: Client, message: Message):
    try:
        if not message.reply_to_message:
            return await message.reply("<b>Reply is required for this command</b>")
        if message.reply_to_message.photo:
            filename = "circle.jpg"
            typ = "photo"
        elif message.reply_to_message.sticker:
            if message.reply_to_message.sticker.is_video:
                return await message.reply("<b>Video stickers is not supported</b>")
            filename = "circle.webp"
            typ = "photo"
        elif message.reply_to_message.video:
            filename = "circle.mp4"
            typ = "video"
        elif message.reply_to_message.document:
            _filename = message.reply_to_message.document.file_name.casefold()
            if _filename.endswith(".png"):
                filename = "circle.png"
                typ = "photo"
            elif _filename.endswith(".jpg"):
                filename = "circle.jpg"
                typ = "photo"
            elif _filename.endswith(".jpeg"):
                filename = "circle.jpeg"
                typ = "photo"
            elif _filename.endswith(".webp"):
                filename = "circle.webp"
                typ = "photo"
            elif _filename.endswith(".mp4"):
                filename = "circle.mp4"
                typ = "video"
            else:
                return await message.reply("<b>Invalid file type</b>")
        else:
            return await message.reply("<b>Invalid file type</b>")

        if typ == "photo":
            await message.edit("<b>Processing image</b>📷")
            await message.reply_to_message.download(f"downloads/{filename}")
            await asyncio.get_event_loop().run_in_executor(None, process_img, filename)
            await message.delete()
            return await message.reply_sticker(
                sticker=im, reply_to_message_id=message.reply_to_message.message_id
            )
        else:
            await message.edit("<b>Processing video</b>🎥")
            await message.reply_to_message.download(f"downloads/{filename}")
            await asyncio.get_event_loop().run_in_executor(None, process_vid, filename)

            await message.edit("<b>Saving video</b>📼")
            await asyncio.get_event_loop().run_in_executor(None, video.write_videofile, "downloads/result.mp4")

            await message.delete()
            await message.reply_video_note(
                video_note="downloads/result.mp4",
                duration=int(video.duration),
                reply_to_message_id=message.reply_to_message.message_id,
            )
            os.remove(f"downloads/{filename}")
            os.remove("downloads/result.mp4")
    except Exception as e:
        await message.reply(format_exc(e))


modules_help["circle"] = {"round": "Закруглить фото или видео."}
