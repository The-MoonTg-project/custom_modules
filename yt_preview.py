import urllib

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

MAX_URL = "https://img.youtube.com/vi/{id}/maxresdefault.jpg"
HQ_URL = "https://img.youtube.com/vi/{id}/hqdefault.jpg"


def get_video_id(url):
    try:
        return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["v"][0]
    except Exception:
        return url.replace("&feature=share", "").split("/")[-1]


@Client.on_message(filters.command("preview", prefix) & filters.me)
async def preview(client: Client, message: Message):
    try:
        if message.reply_to_message:
            video_id = get_video_id(message.reply_to_message.text)
            video_id = MAX_URL.format(id=video_id)
            await message.edit("Upload Preview")
            await client.send_photo(
                message.chat.id,
                video_id,
                caption=f"<a href='{video_id}'>Download Link</a>",
                parse_mode="HTML",
            )
            await message.delete()
        elif len(message.command) == 2:
            video_id = get_video_id(message.command[1])
            video_id = MAX_URL.format(id=video_id)
            await message.edit("Upload Preview")
            await client.send_photo(
                message.chat.id,
                video_id,
                caption=f"<a href='{video_id}'>Download Link</a>",
                parse_mode="HTML",
            )
            await message.delete()
        elif len(message.command) == 3:
            video_id = get_video_id(message.command[1])
            video_id = MAX_URL.format(id=video_id)
            view = message.command[2]
            await message.edit("Upload Preview")
            if view == "1":
                await client.send_photo(
                    message.chat.id,
                    video_id,
                    caption=f"<a href='{video_id}'>Download Link</a>",
                    parse_mode="HTML",
                )
                await message.delete()
            elif view == "2":
                await client.send_photo(
                    message.chat.id, video_id, caption=f"Download Link - {video_id}"
                )
                await message.delete()
            elif view == "3":
                await client.send_photo(
                    message.chat.id, video_id, caption=f"{video_id}"
                )
                await message.delete()
            elif view == "4":
                await client.send_photo(message.chat.id, video_id)
                await message.delete()
            elif view == "5":
                captionText = message.command[3:]
                captionText = " ".join(captionText)
                await client.send_photo(
                    message.chat.id,
                    video_id,
                    caption=f"<a href='{video_id}'>{captionText}</a>",
                    parse_mode="HTML",
                )
                await message.delete()
    except:
        await message.edit(f"This <a href='{video_id}'>link</a> does not exist")


modules_help["yt_preview"] = {
    "preview [link]* 1/2/3/4/5": "Download the preview from the link\n"
    "1 - Preview, link\n"
    "2 - Download link\n"
    "3 - link\n"
    "4 - Preview, ling\n"
    "5 - Preview Your Text"
}
