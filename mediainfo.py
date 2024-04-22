# NOTE: If you're on local installation then you'll need `mediainfo` installed in your system
# If you're on heroku then make sure to install `mediainfo` buildpacks
# Others installations like docker users doesn;t need to install anything

import os
import time
import datetime
import subprocess
import asyncio
import requests

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import prefix, modules_help
from utils.scripts import format_exc, progress, edit_or_reply, import_library



async def telegraph(user_name, content):
    url = 'https://api.safone.dev'

    formatted_content = '<br>'.join(content.split('\n'))
    formatted_content = '<p>' + formatted_content + '</p>'

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://api.safone.dev/docs',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'accept': 'application/json',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }

    data = {
    "title": "MediaInfo",
    "content": formatted_content,
    "author_name": user_name
    }

    response = requests.post(url=f"{url}/telegraph/text", headers=headers, json=data, timeout=5)

    result = response.json()

    return result['url']



@Client.on_message(filters.command("mediainfo", prefix) & filters.me)
async def mediainfo(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("Kindly Reply to a File")
    
    try:
        user_name = message.from_user.id
        ms = await edit_or_reply(message, '`Downloading...')
        ct = time.time()
        file_path = await message.reply_to_message.download(progress=progress, progress_args=(ms, ct, 'Downloading...'))
        await ms.edit_text(f"<code>Trying to open file...</code>")
        file_info = os.stat(file_path)
        file_name = file_path.split('/')[-1:]
        file_size = file_info.st_size
        last_modified = datetime.datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        paste = subprocess.run(['mediainfo', '-f', file_path], capture_output=True, text=True)
        result = paste.stdout
        content = await telegraph(user_name=user_name, content=result)
        await ms.edit_text(
            f"**File Name:** `{file_name[0]}`\n**Size:** `{file_size} bytes`\n**Last Modified:** `{last_modified}`\n**Result:** {content}",
            parse_mode=enums.ParseMode.MARKDOWN)

    except Exception as e:
        await ms.edit_text(format_exc(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

modules_help["mediainfo"] = {
    "mediainfo [reply_to_file]*": "Get MediaInfo result of any file"
}
