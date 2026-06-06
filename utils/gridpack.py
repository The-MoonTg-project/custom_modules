import io
import os
import string
import random
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.scripts import import_library

import_library("PIL", "Pillow")
from PIL import Image


async def crop_and_divide(img):
    (width, height) = img.size
    rows = 5
    columns = 5
    scale_width = width // columns
    scale_height = height // rows
    if (scale_width * columns, scale_height * rows) != (width, height):
        img = img.resize((scale_width * columns, scale_height * rows))
    (new_width, new_height) = (0, 0)
    media = []
    for _ in range(1, rows + 1):
        for o in range(1, columns + 1):
            mimg = img.crop(
                (
                    new_width,
                    new_height,
                    new_width + scale_width,
                    new_height + scale_height,
                )
            )
            mimg = mimg.resize((512, 512))
            image = io.BytesIO()
            image.name = "Friday.png"
            mimg.save(image, "PNG")
            media.append(image.getvalue())
            new_width += scale_width
        new_width = 0
        new_height += scale_height
    return media


@Client.on_message(filters.command("gridpack", prefix) & filters.me)
async def make_grid(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("`Reply to a Photo :(`")
        return
    pic = message.reply_to_message.photo
    if not pic:
        await message.edit("`Reply to a Photo :(`")
        return

    input_text = ""
    if len(message.command) > 1:
        input_text = message.text.split(None, 1)[1]

    if not input_text or "|" not in input_text:
        await message.edit("**Invalid Syntax:**\n**Format:** `.gridpack pack name|emoji`")
        return

    kk = input_text.split("|")
    pack = kk[0].strip()
    stcr = kk[1].strip()

    op = await message.edit("`Making gridpack 🔪`\n__🔪Cropping and adjusting the image...__")

    ok = await client.download_media(message.reply_to_message)

    emoji = stcr
    name = "FridayUB_" + "".join(
        random.choice(list(string.ascii_lowercase + string.ascii_uppercase))
        for _ in range(16)
    )

    image = Image.open(ok)
    w, h = image.size
    www = max(w, h)
    img = Image.new("RGBA", (www, www), (0, 0, 0, 0))
    img.paste(image, ((www - w) // 2, 0))
    newimg = img.resize((100, 100))
    new_img = io.BytesIO()
    new_img.name = name + ".png"
    images = await crop_and_divide(img)
    newimg.save(new_img, "PNG")
    new_img.seek(0)

    await op.edit("__Making the pack...__")
    i = 0

    await client.send_message("stickers", "/cancel")
    await asyncio.sleep(0.5)
    await client.send_message("stickers", "/newpack")
    await asyncio.sleep(0.5)
    await client.send_message("stickers", pack)
    await asyncio.sleep(0.5)

    for im in images:
        img_bytes = io.BytesIO(im)
        img_bytes.name = name + ".png"
        img_bytes.seek(0)
        await client.send_document("stickers", img_bytes)
        await asyncio.sleep(0.5)
        await client.send_message("stickers", stcr)
        await asyncio.sleep(0.5)
        i += 1
        await op.edit(f"__Making the pack.\nProgress: {i}/{len(images)}__")

    await client.send_message("stickers", "/publish")
    await asyncio.sleep(0.5)
    await client.send_message("stickers", "/skip")
    await asyncio.sleep(0.5)
    await client.send_message("stickers", name)
    await asyncio.sleep(0.5)

    link = f"https://t.me/addstickers/{name}"
    await op.edit(
        f"__Successfully Created Gridpack\nYou can find it Here :-__ [{pack}]({link})\n\n__**By @FridayUB**__",
        disable_web_page_preview=True,
    )
    if os.path.exists(ok):
        os.remove(ok)


modules_help["gridpack"] = {
    "gridpack [pack name]|[emoji]": "Create a sticker pack of an image in a cool way"
}
