# Original module author: t.me/KeyZenD
# Adaptation for Dragon-Userbot by t.me/AmokDev (github.com/AmokDev)

from io import BytesIO
from random import randint

from pyrogram import Client, filters
from pyrogram.types import Message

from requests import get
from PIL import Image, ImageFont, ImageDraw
from textwrap import wrap

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("amogus", prefix) & filters.me)
async def amogus(client: Client, message: Message):
    text = " ".join(message.command[1:])

    await message.edit("<b>amgus, tun tun tun tun tun tun tun tudududn tun tun...</b>")

    clr = randint(1, 12)

    url = "https://raw.githubusercontent.com/KeyZenD/AmongUs/master/"
    font = ImageFont.truetype(BytesIO(get(url + "bold.ttf").content), 60)
    imposter = Image.open(BytesIO(get(f"{url}{clr}.png").content))

    text_ = "\n".join(["\n".join(wrap(part, 30)) for part in text.split("\n")])
    w, h = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textsize(
        text_, font, stroke_width=2
    )
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
