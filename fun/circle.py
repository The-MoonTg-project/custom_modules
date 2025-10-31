import os
import tempfile
import json
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

async def run_subprocess(cmd, timeout=None):
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout)
        return proc.returncode, stdout.decode(), stderr.decode()
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        raise

async def get_video_duration(video_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", video_path
    ]
    try:
        returncode, stdout, _ = await run_subprocess(cmd, timeout=20)
        if returncode != 0 or not stdout:
            return 10
        return min(float(json.loads(stdout)["format"]["duration"]), 60)
    except Exception:
        return 10

@Client.on_message(filters.command("circle", prefix) & filters.me)
async def send_circle_video(client: Client, message: Message):
    reply = getattr(message, "reply_to_message", None)
    if not reply or not (reply.video or reply.animation or reply.document):
        await message.edit("Reply to a video.")
        return

    parts = message.text.strip().split()
    target_username = parts[1] if len(parts) >= 2 and parts[1].startswith("@") else None
    send_to_current_chat = target_username is None

    if len(parts) >= 2 and not parts[1].startswith("@"):
        await message.edit("`.circle` or `.circle @user`")
        return

    await message.edit("Downloading...")

    video_path = circle_path = None
    try:
        video_path = await client.download_media(reply)
        if not video_path:
            await message.edit("Download failed.")
            return

        video_duration = await get_video_duration(video_path)

        with tempfile.NamedTemporaryFile(suffix='_circle.mp4', delete=False) as temp_file:
            circle_path = temp_file.name

        await message.edit("Processing...")

        # Use higher bitrate and better scaling algorithm to reduce blurriness
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-filter_complex",
            (
                "[0:v]scale=640:640:force_original_aspect_ratio=increase:flags=lanczos,"
                "crop=640:640[scaled];"
                "color=white:size=640x640[c];"
                "[scaled]format=rgba,"
                "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                "a='if(gte(hypot(X-320,Y-320),320),0,255)'[masked];"
                "[c][masked]overlay=0:0"
            ),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:v", "2000k", "-b:a", "128k",
            "-r", "30", "-t", str(video_duration),
            "-preset", "ultrafast", "-movflags", "+faststart",
            circle_path
        ]

        returncode, _, stderr = await run_subprocess(cmd, timeout=300)
        if returncode != 0 or not os.path.exists(circle_path) or os.path.getsize(circle_path) == 0:
            await message.edit("FFmpeg error." if returncode != 0 else "Convert failed.")
            return

        await message.edit("Sending...")
        send_kwargs = dict(
            video_note=circle_path, duration=int(video_duration), length=640
        )
        try:
            if send_to_current_chat:
                await client.send_video_note(chat_id=message.chat.id, **send_kwargs)
                await message.edit("Done!")
            else:
                await client.send_video_note(chat_id=target_username, **send_kwargs)
                await message.edit(f"Sent to {target_username}")
        except Exception as e:
            await message.edit("Send failed.")

    except asyncio.TimeoutError:
        await message.edit("Timeout.")
    except Exception as e:
        await message.edit("Error.")
    finally:
        for path in (video_path, circle_path):
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
                
modules_help["circle"] = {
    "circle": "Convert video to circle. High quality and less blurry."
}
