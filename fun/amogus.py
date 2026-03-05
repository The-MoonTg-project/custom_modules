# Original module author: t.me/KeyZenD
# Adaptation for Dragon-Userbot by t.me/AmokDev (github.com/AmokDev)
# Adaptation for Moon-Userbot by Abhi

from io import BytesIO
from random import randint
from textwrap import wrap

import aiohttp
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils import modules_help, prefix


@Client.on_message(filters.command("amogus", prefix) & filters.me)
async def amogus(client: Client, message: Message):
    text = " ".join(message.command[1:])

    await message.edit(
        "<b>amgus, tun tun tun tun tun tun tun tudududn tun tun...</b>",
        parse_mode=enums.ParseMode.HTML,
    )

    clr = randint(1, 12)

    url = "https://raw.githubusercontent.com/The-MoonTg-project/AmongUs/master/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url + "bold.ttf") as resp:
            font_data = await resp.read()
        async with session.get(f"{url}{clr}.png") as resp:
            imposter_data = await resp.read()

    font = ImageFont.truetype(BytesIO(font_data), 60)
    imposter = Image.open(BytesIO(imposter_data))

    text_ = "\n".join(["\n".join(wrap(part, 30)) for part in text.split("\n")])
    bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textbbox(
        (0, 0), text_, font, stroke_width=2
    )
    # w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    w, h = bbox[2], bbox[3]
    text = Image.new("RGBA", (w + 30, h + 30))
    ImageDraw.Draw(text).multiline_text(
        (15, 15), text_, "#FFF", font, stroke_width=2, stroke_fill="#000"
    )
    w = imposter.width + text.width + 10
    h = max(imposter.height, text.height)

    image = Image.new("RGBA", (w, h))
    image.paste(imposter, (0, h - imposter.height), imposter)
    image.paste(text, (w - text.width, 0), text)
    image.thumbnail((512, 512))

    output = BytesIO()
    output.name = "imposter.webp"
    image.save(output)
    output.seek(0)

    await message.delete()
    await client.send_sticker(message.chat.id, output)


modules_help["amogus"] = {
    "amogus [text]": "amgus, tun tun tun tun tun tun tun tudududn tun tun"
}
