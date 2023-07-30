from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message

from utils.misc import modules_help, prefix

def ReplyCheck(message: Message):
    reply_id = None

    if message.reply_to_message:
        reply_id = message.reply_to_message.id

    elif not message.from_user.is_self:
        reply_id = message.id

    return reply_id

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
async def compress(client: Client, message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.edit("**Please Reply To A Video**")
        return
    if replied.media == MessageMediaType.VIDEO:
        await message.edit("`Downloading Video . . .`")
        file = await client.download_media(
            message=replied,
            file_name="Moon-Userbot/resources/",
        )
        replied.video.duration
        out_file = file
        try:
            await message.edit("`Trying to compress. . .`")
            prefix = f"ffmpeg -i {file} -vcodec libx264 -crf 24 {out_file}"
            await run_cmd(prefix)
            await message.edit("`Uploading File . . .`")
            await message.delete()
            await client.send_document(
                message.chat.id,
                avid=out_file,
                reply_to_message_id=ReplyCheck(message),
            )
        except BaseException as e:
            await message.edit(f"**INFO:** `{e}`")
    else:
        await message.edit("**Please Reply To A Video**")
        return
