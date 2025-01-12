import math
import os
import re
import time
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from subprocess import Popen, PIPE

from utils.misc import modules_help, prefix
from utils.scripts import (
    humanbytes,
    time_formatter,
    with_reply,
    format_exc,
    edit_or_reply,
)
from utils.scripts import progress as pg


@Client.on_message(filters.command("compress", prefix) & filters.me)
@with_reply
async def compress(client: Client, message: Message):
    replied = message.reply_to_message
    if not replied.media:
        await edit_or_reply(message, "<b>Please Reply To A Video</b>")
        return
    if replied.media:
        c_time = time.time()
        ms_ = await edit_or_reply(
            message,
            "<code>Downloading Video . . .</code>",
        )
        file = await client.download_media(
            message=replied,
            file_name="resources/",
            progress=pg,
            progress_args=(ms_, c_time, "`Downloading This File!`"),
        )
        # replied.media.duration
        # d_time = time.time()
        out_file = file + ".mp4"
        file_stats = os.stat(file)
        file_size = file_stats.st_size
        progress = f"progress{file_stats.st_ctime}.txt"
        mdi_cmd = f'mediainfo --fullscan {file} | grep "Frame count"'
        cmd_obj = Popen(
            mdi_cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )
        stdout = cmd_obj.communicate(timeout=60)
        x, y = stdout
        if y and y.endswith("NOT_FOUND"):
            return await edit_or_reply(message, f"ERROR: `{y}`")
        total_frames = x.split(":")[1].split("\n")[0]
        try:
            if len(message.command) > 1:
                crf = message.text.split(maxsplit=1)[1]
            else:
                crf = 24
            await edit_or_reply(
                message,
                "<code>Trying to compress. . .</code>",
            )
            # await message.edit("<code>If video size is big it'll take a while please be patient</code>")
            with open(progress, "w"):
                pass
            proce = await asyncio.create_subprocess_shell(
                f"ffmpeg -hide_banner -loglevel quiet -progress {progress} -i {file} -preset ultrafast -vcodec libx265 -crf {crf} {out_file}",
                stdout=PIPE,
                stderr=PIPE,
            )
            while proce.returncode != 0:
                await asyncio.sleep(3)
                with open(progress, "r+") as fil:
                    text = fil.read()
                    frames = re.findall("frame=(\\d+)", text)
                    size = re.findall("total_size=(\\d+)", text)
                    speed = 0
                    if len(frames):
                        elapse = int(frames[-1])
                    if len(size):
                        size = int(size[-1])
                        per = elapse * 100 / int(total_frames)
                        time_diff = time.time() - int(time.time())
                        speed = round(elapse / time_diff, 2)
                    if int(speed) != 0:
                        some_eta = ((int(total_frames) - elapse) / speed) * 1000
                        text = f"<code>Compressing {file} at {crf} CRF.\n</code>"
                        progress_str = "<code>[{0}{1}] {2}%\n\n</code>".format(
                            "".join("●" for _ in range(math.floor(per / 5))),
                            "".join("" for _ in range(20 - math.floor(per / 5))),
                            round(per, 2),
                        )

                        e_size = (
                            f"{humanbytes(size)} of ~{humanbytes((size / per) * 100)}"
                        )
                        eta = f"~{time_formatter(some_eta)}"
                        try:
                            await edit_or_reply(
                                message,
                                text
                                + progress_str
                                + "<code>"
                                + e_size
                                + "</code>"
                                + "\n\n<code>"
                                + eta
                                + "</code>",
                            )
                        except Exception as e:
                            await message.edit_text(format_exc(e))
            out_file_stats = os.stat(out_file)
            out_file_size = out_file_stats.st_size
            com_time = time.time()
            difff = time_formatter((com_time - c_time) * 1000)
            await edit_or_reply(
                message,
                f"<code>Compressed {humanbytes(file_size)} to {humanbytes(out_file_size)}, Uploading Now . . .</code>",
            )
            # await message.delete()
            differ = 100 - ((out_file_size / file_size) * 100)
            await client.send_document(
                message.chat.id,
                out_file,
                progress=pg,
                progress_args=(ms_, c_time, "`Uploading...`"),
                caption=f"<b>Original Size:</b> <code>{humanbytes(file_size)}MB</code>\n<b>Compressed Size:</b> <code>{humanbytes(out_file_size)}</code>\n<b>Compression Ratio:</b> <code>{differ:.2f}%</code>\n <b>Time Taken To Compress:</b> <code>{difff}</code>",
                reply_to_message_id=message.id,
            )
        except BaseException as e:
            await edit_or_reply(
                message,
                f"<b>INFO:</b> <code>{e}</code>",
            )
        finally:
            os.remove(file)
            os.remove(out_file)
            os.remove(progress)
    else:
        await edit_or_reply(message, "<b>Please Reply To A Video</b>")
        return


modules_help["compress"] = {
    "compress [crf value]": "reply to a video to compress it :)\ncrf value is optional if not given default will be used"
}
