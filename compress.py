import os
import sys
from typing import Tuple
import shlex
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import with_reply

async def run_cmd(prefix: str) -> Tuple[str, str, int, int]:
    """Run Commands"""
    args = shlex.split(prefix)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )

@Client.on_message(filters.command("compress", prefix) & filters.me)
@with_reply
async def compress(client: Client, message: Message):
    replied = message.reply_to_message
    if not replied.media:
        await message.edit("**Please Reply To A Video**")
        return
    if replied.media:
        await message.edit("`Downloading Video . . .`")
        file = await client.download_media(
            message=replied,
            file_name="resources/",
        )
        #replied.media.duration
        out_file = file
        try:
            await message.edit("`Trying to compress. . .`")
            await message.edit("`If video size is big it'll take a while please be patient`")
            cmp = f"ffmpeg -i {file} -vcodec libx265 -crf 24 {out_file}"
            await run_cmd(cmp)
            await message.edit("`Uploading File . . .`")
            await message.delete()
            await client.send_document(message.chat.id, out_file)
        except BaseException as e:
            await message.edit(f"**INFO:** `{e}`")
        finally:
            os.remove(file)
    else:
        await message.edit("**Please Reply To A Video**")
        return

modules_help["compress"] = {
    "compress": f"reply to a video to compress it :)"
}
