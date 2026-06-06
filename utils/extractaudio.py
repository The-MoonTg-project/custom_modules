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
        await op.edit("`Generating waveform...`")
        with open(audio_path, "rb") as f:
            audio_data = f.read()
            
        try:
            from utils.scripts import generate_waveform
            waveform, duration = await generate_waveform(audio_data)
        except Exception:
            waveform, duration = None, 0
            
        await op.edit("`Uploading extracted audio...`")
        
        # Determine mime type
        mime_type = "audio/mpeg"
        if audio_format in ("ogg", "opus"):
            mime_type = "audio/ogg"
        elif audio_format == "wav":
            mime_type = "audio/x-wav"
        elif audio_format == "flac":
            mime_type = "audio/flac"
            
        import random
        from pyrogram.raw.functions.messages import SendMedia
        from pyrogram.raw.types import DocumentAttributeAudio, InputMediaUploadedDocument
        
        file = await client.save_file(audio_path)
        attr = DocumentAttributeAudio(duration=duration, voice=False, waveform=waveform)
        media = InputMediaUploadedDocument(file=file, mime_type=mime_type, attributes=[attr])
        peer = await client.resolve_peer(message.chat.id)
        
        await client.invoke(
            SendMedia(
                peer=peer, 
                media=media, 
                message="**Audio Extracted**\nPowered By @moonuserbot", 
                random_id=random.randint(1, 2**63)
            )
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
