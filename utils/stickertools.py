import os
from PIL import Image

from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix

async def convert_to_image(message: Message, client: Client):
    file = await client.download_media(message.reply_to_message)
    if not file:
        return None
    if file.endswith(".webp"):
        img = Image.open(file).convert("RGBA")
        new_file = file + ".png"
        img.save(new_file, "PNG")
        os.remove(file)
        return new_file
    return file

@Client.on_message(filters.command("stoi", prefix) & filters.me)
async def stcr_to_img(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("`Reply to a sticker!`")
        return
    mg = await message.edit("`Processing...`")
    img = await convert_to_image(message, client)
    if not img:
        await mg.edit("`Failed to download media.`")
        return
    await client.send_photo(
        message.chat.id, 
        img, 
        reply_to_message_id=message.reply_to_message.id
    )
    await mg.delete()
    if os.path.exists(img):
        os.remove(img)

@Client.on_message(filters.command("stof", prefix) & filters.me)
async def stcr_to_png(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("`Reply to a sticker!`")
        return
    mg = await message.edit("`Processing...`")
    img = await convert_to_image(message, client)
    if not img:
        await mg.edit("`Failed to download media.`")
        return
    await client.send_document(
        message.chat.id, 
        img, 
        reply_to_message_id=message.reply_to_message.id
    )
    await mg.delete()
    if os.path.exists(img):
        os.remove(img)

@Client.on_message(filters.command("ftoi", prefix) & filters.me)
async def file_to_img(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("`Reply to a file!`")
        return
    mg = await message.edit("`Processing...`")
    op = message.reply_to_message
    img = await client.download_media(op)
    if not img:
        await mg.edit("`Failed to download media.`")
        return
    await client.send_photo(
        message.chat.id, 
        img, 
        reply_to_message_id=message.reply_to_message.id
    )
    await mg.delete()
    if os.path.exists(img):
        os.remove(img)

@Client.on_message(filters.command("itos", prefix) & filters.me)
async def img_to_stcr(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("`Reply to an image!`")
        return
    mg = await message.edit("`Processing...`")
    stcr = message.reply_to_message
    ok = await client.download_media(stcr)
    if not ok:
        await mg.edit("`Failed to download media.`")
        return
    
    try:
        img = Image.open(ok).convert("RGBA")
        img.thumbnail((512, 512))
        webp_file = "moonub.webp"
        img.save(webp_file, "WEBP")
        
        await client.send_document(
            message.chat.id, 
            webp_file, 
            reply_to_message_id=message.reply_to_message.id
        )
    except Exception as e:
        await mg.edit(f"`Error:` {e}")
    finally:
        await mg.delete()
        if os.path.exists(ok):
            os.remove(ok)
        if os.path.exists("moonub.webp"):
            os.remove("moonub.webp")

@Client.on_message(filters.command("itof", prefix) & filters.me)
async def img_to_file(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("`Reply to an image!`")
        return
    mg = await message.edit("`Processing...`")
    op = message.reply_to_message
    img = await client.download_media(op)
    if not img:
        await mg.edit("`Failed to download media.`")
        return
    await client.send_document(
        message.chat.id, 
        img, 
        reply_to_message_id=message.reply_to_message.id
    )
    await mg.delete()
    if os.path.exists(img):
        os.remove(img)


modules_help["stickertools"] = {
    "stoi": "Converts sticker to image",
    "stof": "Converts sticker to file format",
    "ftoi": "Converts a file to image",
    "itos": "Converts image to sticker",
    "itof": "Converts an image to file"
}
