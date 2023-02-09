# original module https://raw.githubusercontent.com/KeyZenD/modules/master/MirrorFlipV2.py | t.me/the_kzd
import os


from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import import_library

PIL = import_library("PIL", "pillow")
from PIL import Image, ImageOps


async def make(client, message, o):
    reply = message.reply_to_message
    if reply.photo or reply.sticker:
        if reply.photo:
            downloads = await client.download_media(reply.photo.file_id)
        else:
            downloads = await client.download_media(reply.sticker.file_id)
        path = f"{downloads}"
        img = Image.open(path)
        await message.delete()
        w, h = img.size
        if o in [1, 2]:
            if o == 2:
                img = ImageOps.mirror(img)
            part = img.crop([0, 0, w // 2, h])
            img = ImageOps.mirror(img)
        else:
            if o == 4:
                img = ImageOps.flip(img)
            part = img.crop([0, 0, w, h // 2])
            img = ImageOps.flip(img)
        img.paste(part, (0, 0))
        img.save(path)
        if reply.photo:
            return await reply.reply_photo(photo=path)
        elif reply.sticker:
            return await reply.reply_sticker(sticker=path)
        os.remove(path)

    return await message.edit("<b>Need to answer the photo/sticker</b>")


@Client.on_message(filters.command(["ll", "rr", "dd", "uu"], prefix) & filters.me)
async def mirror_flip(client: Client, message: Message):
    await message.edit("<b>Processing...</b>")
    param = {"ll": 1, "rr": 2, "dd": 3, "uu": 4}[message.command[0]]
    await make(client, message, param)


modules_help["mirror_flip"] = {
    "ll [reply on photo or sticker]*": "reflects the left side",
    "rr [reply on photo or sticker]*": "reflects the right side",
    "uu [reply on photo or sticker]*": "reflects the top",
    "dd [reply on photo or sticker]*": "reflects the bottom",
}
