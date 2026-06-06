import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix

@Client.on_message(filters.command(["ext", "extract"], prefix) & filters.me)
async def extract_audio(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("`Please Provide an Audio format (e.g. mp3, wav, flac)!`")
        return
        
    audio_format = message.command[1].lower().strip(".")
    
    if not message.reply_to_message:
        await message.edit("`Reply to a Video!`")
        return
        
    if not message.reply_to_message.video and not message.reply_to_message.document:
        await message.edit("`Reply to a Video to Extract audio.`")
        return
        
    op = await message.edit("`Downloading media...`")
    
    file_path = await message.reply_to_message.download()
    
    if not file_path:
        await op.edit("`Failed to download media.`")
        return
        
    await op.edit("`Extracting Audio, please wait...`")
        
    audio_path = str(os.path.basename(file_path)).rsplit(".", 1)[0] + f".{audio_format}"

    cmd = f"ffmpeg -i '{file_path}' -q:a 0 -map 0:a '{audio_path}' -y"

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    await process.communicate()
    
    if os.path.exists(audio_path):
        await op.edit("`Uploading extracted audio...`")
        await client.send_audio(
            message.chat.id, 
            audio_path, 
            caption="**Audio Extracted**\nPowered By @MoonUB",
            reply_to_message_id=message.reply_to_message.id
        )
        await op.delete()
        os.remove(file_path)
        os.remove(audio_path)
    else:
        await op.edit("`Failed to extract audio. Are you sure the video has an audio track?`")
        if os.path.exists(file_path):
            os.remove(file_path)

modules_help["extractaudio"] = {
    "ext [format]": "Reply to a video file to extract audio in the specified format (mp3, wav, flac, etc.).",
    "extract [format]": "Alias for ext command."
}
