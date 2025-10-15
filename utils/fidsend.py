import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("fidsend", prefix) & filters.me)
async def fidsend(_, message: Message):
    if len(message.command) <= 1:
        return
    
    file_id = " ".join(message.command[1:])
    
    try:
        try:
            await message.reply_photo(file_id)
        except:
            try:
                await message.reply_video(file_id)
            except:
                try:
                    await message.reply_sticker(file_id)
                except:
                    try:
                        await message.reply_voice(file_id)
                    except:
                        try:
                            await message.reply_video_note(file_id)
                        except:
                            try:
                                await message.reply_audio(file_id)
                            except:
                                try:
                                    await message.reply_animation(file_id)
                                except:
                                    await message.reply_document(file_id)
        
        await message.delete()
    except Exception as e:
        await message.edit(
            f"<b>Error:</b> <code>{e}</code>",
            parse_mode=enums.ParseMode.HTML,
        )

modules_help["file_sender"] = {
    "fidsend [file_id]*": "send any media file using its file ID\nSupports: photo, video, sticker, voice, video note, audio, animation, document"
}