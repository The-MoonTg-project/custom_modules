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

import time
import os
import datetime
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    ChatForwardsRestricted,
    PeerIdInvalid,
    MessageIdInvalid,
    MessageTooLong,
    FloodWait
)
from pyrogram.enums import MessageMediaType

from utils.misc import modules_help, prefix
from utils.scripts import format_exc

class ProgressTracker:
    def __init__(self):
        self.last_update = 0
        self.update_interval = 1
        
    def should_update(self):
        now = time.time()
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            return True
        return False

progress_tracker = ProgressTracker()

async def safe_edit(xx: Message, text: str):
    try:
        if progress_tracker.should_update():
            await xx.edit(text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass

def calculate_eta(current: int, total: int, start_time: float) -> str:
    try:
        elapsed = time.time() - start_time
        if elapsed < 0.1 or total == 0:
            return "N/A"
        
        speed = current / elapsed
        remaining = total - current
        eta = remaining / speed
        return str(datetime.timedelta(seconds=int(eta)))
    except:
        return "N/A"

@Client.on_message(filters.command("getmsg", prefix) & filters.me)
async def get_restricted_msg(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("❗ Please provide a link!")
    
    link = message.command[1]
    xx = await message.edit("🔄 Initializing...")
    
    chat, msg_id = get_chat_and_msgid(link)
    if not (chat and msg_id):
        return await xx.edit("❌ Invalid link format!\nExample: https://t.me/c/1524685769/40392")

    try:
        msg = await client.get_messages(chat, msg_id)
    except Exception as e:
        return await xx.edit(f"🚫 Error retrieving message:\n`{format_exc(e)}`")

    if not msg:
        return await xx.edit("❌ Message not found")

    # Try to copy message first
    try:
        await msg.copy(message.chat.id)
        return await xx.delete()
    except ChatForwardsRestricted:
        pass
    except Exception as e:
        await xx.edit(f"⚠️ Forward restricted, trying alternative method...")

    # Handle media content
    if msg.media:
        media_path = None
        try:
            # Download with progress
            dl_start = time.time()
            
            async def dl_progress(current, total):
                text = (
                    f"⬇️ Downloading...\n"
                    f"`{current * 100 / total:.1f}%` | "
                    f"ETA: `{calculate_eta(current, total, dl_start)}`"
                )
                await safe_edit(xx, text)

            media_path = await msg.download(progress=dl_progress)

            # Upload with original formatting
            upload_start = time.time()
            
            async def up_progress(current, total):
                text = (
                    f"⬆️ Uploading...\n"
                    f"`{current * 100 / total:.1f}%` | "
                    f"ETA: `{calculate_eta(current, total, upload_start)}`"
                )
                await safe_edit(xx, text)

            common_args = {
                "caption": msg.caption or "",
                "caption_entities": msg.caption_entities or [],
                "progress": up_progress
            }

            if msg.media == MessageMediaType.VIDEO:
                await client.send_video(
                    message.chat.id,
                    media_path,
                    duration=msg.video.duration,
                    width=msg.video.width,
                    height=msg.video.height,
                    supports_streaming=True,
                    **common_args
                )
            elif msg.media == MessageMediaType.PHOTO:
                await client.send_photo(
                    message.chat.id,
                    media_path,
                    **common_args
                )
            else:
                await client.send_document(
                    message.chat.id,
                    media_path,
                    force_document=False,
                    **common_args
                )

            await xx.delete()
        except Exception as e:
            await xx.edit(f"❌ Error processing media:\n`{format_exc(e)}`")
        finally:
            if media_path and os.path.exists(media_path):
                try:
                    os.remove(media_path)
                except Exception as e:
                    print(f"Error deleting file: {e}")
    else:
        # Handle text messages with formatting
        try:
            await xx.edit(
                f"📝 **Message content:**\n\n{msg.text}",
                entities=msg.entities or []
            )
        except MessageTooLong:
            txt_path = os.path.abspath("message.txt")
            try:
                with open(txt_path, "w") as f:
                    f.write(msg.text)
                await client.send_document(
                    message.chat.id,
                    txt_path,
                    caption="Original message formatting preserved in file"
                )
                await xx.delete()
            finally:
                if txt_path and os.path.exists(txt_path):
                    try:
                        os.remove(txt_path)
                    except Exception as e:
                        print(f"Error deleting text file: {e}")

def get_chat_and_msgid(link: str) -> Union[tuple, tuple[None, None]]:
    try:
        parts = link.strip("/").split("/")
        if "c" in parts:
            c_index = parts.index("c")
            channel_id = int(parts[c_index + 1])
            msg_id = int(parts[c_index + 2])
            return (-1000000000000 - channel_id), msg_id
        else:
            msg_id = int(parts[-1])
            chat_part = parts[-2]
            return int(chat_part) if chat_part.isdigit() else chat_part, msg_id
    except (ValueError, IndexError, AttributeError):
        return None, None

modules_help["getmsg"] = {
    "getmsg [link]": "Fetch messages with full formatting preservation and cleanup",
}