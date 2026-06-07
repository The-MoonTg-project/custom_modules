import os
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix
from utils.scripts import import_library

# Automatically install noteshrinker if not present
import_library("NoteShrinker", "noteshrinker")

@Client.on_message(filters.command(["hwn"], prefix) & filters.me)
async def hwn(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("`Reply to any Image.`")
        return
        
    is_photo = message.reply_to_message.photo
    is_image_doc = message.reply_to_message.document and message.reply_to_message.document.mime_type.startswith("image/")
    
    if not is_photo and not is_image_doc:
        await message.edit("`Reply to any Image.`")
        return
        
    hmm = await message.edit("`Processing...`")
    
    img_path = await message.reply_to_message.download()
    
    if not img_path:
        await hmm.edit("`Failed to download image.`")
        return
        
    try:
        from NoteShrinker import NoteShrinker
        
        ns = NoteShrinker([img_path])
        shrunk = ns.shrink()
        
        imag_e = "enhanced_image.png"
        for img in shrunk:
            img.save(imag_e)
            
        await client.send_document(
            message.chat.id, 
            imag_e, 
            reply_to_message_id=message.reply_to_message.id
        )
        
        await hmm.delete()
        os.remove(imag_e)
        os.remove(img_path)
        
    except Exception as e:
        await hmm.edit(f"`Error processing image:` {e}")
        if os.path.exists(img_path):
            os.remove(img_path)

modules_help["hwn"] = {
    "hwn": "Reply to an image to enhance it and convert it to a scanned PDF-like NoteShrinker image."
}
