# From CatUB
import asyncio
import re
from io import BytesIO
from random import choice, randint
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont
from click import edit
import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.scripts import edit_or_reply, ReplyCheck
from utils.misc import modules_help, prefix


async def amongus_gen(text: str, clr: int) -> str:
    url = (
        "https://github.com/TgCatUB/CatUserbot-Resources/raw/master/Resources/Amongus/"
    )
    font = ImageFont.truetype(
        BytesIO(
            requests.get(
                "https://github.com/TgCatUB/CatUserbot-Resources/raw/master/Resources/fonts/bold.ttf"
            ).content
        ),
        60,
    )
    imposter = Image.open(BytesIO(requests.get(f"{url}{clr}.png").content))
    text_ = "\n".join("\n".join(wrap(part, 30)) for part in text.split("\n"))
    bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textbbox(
        (0, 0), text_, font, stroke_width=2
    )
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
    image.save(output, "WebP")
    output.seek(0)
    return output


async def get_imposter_img(text: str) -> BytesIO:
    background = requests.get(
        f"https://github.com/TgCatUB/CatUserbot-Resources/raw/master/Resources/imposter/impostor{randint(1, 22)}.png"
    ).content
    font = requests.get(
        "https://github.com/TgCatUB/CatUserbot-Resources/raw/master/Resources/fonts/roboto_regular.ttf"
    ).content
    font = BytesIO(font)
    font = ImageFont.truetype(font, 30)
    image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textbbox(
        (0, 0), text, font, stroke_width=2
    )
    w, h = bbox[2], bbox[3]
    image = Image.open(BytesIO(background))
    x, y = image.size
    draw = ImageDraw.Draw(image)
    draw.multiline_text(
        ((x - w) // 2, (y - h) // 2), text=text, font=font, fill="white", align="center"
    )
    output = BytesIO()
    output.name = "impostor.png"
    image.save(output, "PNG")
    output.seek(0)
    return output


@Client.on_message(filters.command("amongus", prefix) & filters.me)
async def amongus_cmd(client: Client, message: Message):
    text = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    reply = message.reply_to_message
    await message.edit("tun tun tun...")
    if not text and reply:
        text = reply.text or reply.caption or ""

    clr = re.findall(r"-c\d+", text)
    try:
        clr = clr[0]
        clr = clr.replace("-c", "")
        text = text.replace(f"-c{clr}", "")
        clr = int(clr)
        if clr > 12 or clr < 1:
            clr = randint(1, 12)
    except IndexError:
        clr = randint(1, 12)

    if not text:
        if not reply:
            text = f"{message.from_user.first_name} Was a traitor!"
        else:
            text = f"{reply.from_user.first_name} Was a traitor!"

    imposter_file = await amongus_gen(text, clr)
    await message.delete()
    await client.send_sticker(
        message.chat.id,
        imposter_file,
        reply_to_message_id=ReplyCheck(message),
    )


@Client.on_message(filters.command("imposter", prefix) & filters.me)
async def imposter_cmd(client: Client, message: Message):
    remain = randint(1, 2)
    imps = ["wasn't the impostor", "was the impostor"]

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        text = f"{user.first_name} {choice(imps)}."
    else:
        args = message.text.split()[1:]
        if args:
            text = " ".join(args)
        else:
            text = f"{message.from_user.first_name} {choice(imps)}."

    text += f"\n{remain} impostor(s) remain."
    imposter_file = await get_imposter_img(text)
    await message.delete()
    await client.send_photo(
        message.chat.id,
        imposter_file,
        reply_to_message_id=ReplyCheck(message),
    )


@Client.on_message(filters.command(["imp", "impn"], prefix) & filters.me)
async def imp_animation(client: Client, message: Message):
    name = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not name:
        reply = message.reply_to_message
        if reply:
            name = reply.from_user.first_name
        else:
            name = message.from_user.first_name
    cmd = message.command[0].lower()

    text1 = await edit_or_reply(message, "Uhmm... Something is wrong here!!")
    await asyncio.sleep(2)
    await text1.delete()

    stcr1 = await client.send_sticker(message.chat.id, "CAADAQADRwADnjOcH98isYD5RJTwAg")
    text2 = await message.reply(
        f"<b>{message.from_user.first_name}:</b> I have to call discussion"
    )
    await asyncio.sleep(3)
    await stcr1.delete()
    await text2.delete()

    stcr2 = await client.send_sticker(message.chat.id, "CAADAQADRgADnjOcH9odHIXtfgmvAg")
    text3 = await message.reply(
        f"<b>{message.from_user.first_name}:</b> We have to eject the imposter or will lose"
    )
    await asyncio.sleep(3)
    await stcr2.delete()
    await text3.delete()

    stcr3 = await client.send_sticker(message.chat.id, "CAADAQADOwADnjOcH77v3Ap51R7gAg")
    text4 = await message.reply("<b>Others:</b> Where???")
    await asyncio.sleep(2)
    await text4.edit("<b>Others:</b> Who??")
    await asyncio.sleep(2)
    await text4.edit(
        f"<b>{message.from_user.first_name}:</b> Its {name}, I saw {name} using vent"
    )
    await asyncio.sleep(3)
    await text4.edit(f"<b>Others:</b> Okay.. Vote {name}")
    await asyncio.sleep(2)
    await stcr3.delete()
    await text4.delete()

    stcr4 = await client.send_sticker(message.chat.id, "CAADAQADLwADnjOcH-wxu-ehy6NRAg")
    event = await message.reply(f"{name} is ejected.......")

    # Ejection animation
    for _ in range(9):
        await asyncio.sleep(0.5)
        curr_pos = _ + 1
        spaces_before = "ㅤ" * curr_pos
        await event.edit(f"{spaces_before}ඞ{'ㅤ' * (9 - curr_pos)}")

    await asyncio.sleep(0.5)
    await event.edit("ㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    await asyncio.sleep(0.2)
    await stcr4.delete()

    if cmd == "imp":
        text = f". 　　　。　　　　•　 　ﾟ　　。 　　.\n .　　　 　　.　　　　　。　　 。　. 　\n\n  . 　　 。   　     ඞ         。 . 　　 • 　　　　•\n\n  ﾟ{name} was an Imposter.      。　. 　 　       。　.                                        。　. \n                                   　.          。　  　. \n　'         0 Impostor remains    　 。　.  　　.                。　.        。 　     .          。 　            .               .         .    ,      。\n　　ﾟ　　　.　　.    ,　 　。　 　. 　 .     。"
        sticker_id = "CAADAQADLQADnjOcH39IqwyR6Q_0Ag"
    else:
        text = f". 　　　。　　　　•　 　ﾟ　　。 　　.\n .　　　 　　.　　　　　。　　 。　. 　\n\n  . 　　 。   　     ඞ         。 . 　　 • 　　　　•\n\n  ﾟ{name} was not an Imposter.      。　. 　 　       。　.                                        。　. \n                                   　.          。　  　. \n　'         1 Impostor remains    　 。　.  　　.                。　.        。 　     .          。 　            .               .         .    ,      。\n　　ﾟ　　　.　　.    ,　 　。　 　. 　 .     。"
        sticker_id = "CAADAQADQAADnjOcH-WOkB8DEctJAg"

    await event.edit(text)
    await asyncio.sleep(4)
    await event.delete()
    await client.send_sticker(message.chat.id, sticker_id)


modules_help["amongus"] = {
    "amongus": "Create Among Us themed sticker [text/reply] [-c1 to -c12 for colors]",
    "imposter": "Create Among Us imposter image [username/reply]",
    "imp": "Create Among Us ejection animation (imposter)",
    "impn": "Create Among Us ejection animation (not imposter)",
}
