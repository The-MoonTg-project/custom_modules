# NOTE: If you're on local installation then you'll need `mediainfo` installed in your system
# If you're on heroku then make sure to install `mediainfo` buildpacks
# Others installations like docker users doesn't need to install anything

import os
import time
import datetime
import subprocess
import requests

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import prefix, modules_help
from utils.scripts import format_exc, progress, edit_or_reply


async def telegraph(content):
    url = "https://pasty.lus.pm/api/v1/pastes"
    headers = {"User-Agent": "Mozilla/5.0", "content-type": "application/json"}
    data = {"content": content}

    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        paste_id = response.json().get("id")
        if paste_id:
            return f"https://pasty.lus.pm/{paste_id}.txt"
    except Exception:
        pass

    with open("mdf.txt", "w", encoding="utf-8") as f:
        f.write(content)
    return None


@Client.on_message(filters.command("mediainfo", prefix) & filters.me)
async def mediainfo(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("Kindly Reply to a File")
    file_path = None
    try:
        ms = await edit_or_reply(message, "<code>Downloading...</code>")
        ct = time.time()
        file_path = await message.reply_to_message.download(
            progress=progress, progress_args=(ms, ct, "Downloading...")
        )
        await ms.edit_text("<code>Trying to open file...</code>")
        file_info = os.stat(file_path)
        file_name = file_path.split("/")[-1:]
        file_size = file_info.st_size
        last_modified = datetime.datetime.fromtimestamp(file_info.st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        paste = subprocess.run(["mediainfo", file_path], capture_output=True, text=True)
        result = paste.stdout
        content = await telegraph(content=result)
        if content:
            await ms.edit_text(
                f"**File Name:** `{file_name[0]}`\n**Size:** `{file_size} bytes`\n**Last Modified:** `{last_modified}`\n**Result:** {content}",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        else:
            await ms.delete()
            await client.send_document(
                chat_id=message.chat.id,
                document="mdf.txt",
                reply_to_message_id=message.reply_to_message.id,
                caption=f"**File Name:** `{file_name[0]}`\n**Size:** `{file_size} bytes`\n**Last Modified:** `{last_modified}`",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
            if os.path.exists("mdf.txt"):
                os.remove("mdf.txt")
    except Exception as e:
        await ms.edit_text(format_exc(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


modules_help["mediainfo"] = {
    "mediainfo [reply_to_file]*": "Get MediaInfo result of any file"
}
