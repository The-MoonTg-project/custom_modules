from io import BytesIO
from aiohttp import ClientSession
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command("readqr", prefix) & filters.me)
async def readqrcode_handler(client: Client, message: Message):
    try:
        if message.photo:
            filename = await message.download("temp.png")
        elif message.text:
            if not message.reply_to_message:
                return await message.edit(
                    f"Use: <code>{prefix}readqr [reply or photo]</code>",
                    parse_mode=enums.ParseMode.HTML,
                )
            filename = await message.reply_to_message.download("temp.png")
        else:
            return await message.edit(
                f"Use: <code>{prefix}readqr [reply or photo]</code>",
                parse_mode=enums.ParseMode.HTML,
            )

        async with ClientSession() as session:
            async with session.post(
                url2, data={"file": open(filename, "rb").read()}
            ) as response:
                json = await response.json()
                text = json[0]["symbol"][0]["data"]
                if not text:
                    return await message.reply(
                        "<b>Failed to recognize QR code!</b>",
                        parse_mode=enums.ParseMode.HTML,
                    )
                return await message.reply(
                    f"<b>Decrypted text</b>:\n<code>{text}</code>",
                    parse_mode=enums.ParseMode.HTML,
                )
    except Exception as e:
        return await message.reply(format_exc(e), parse_mode=enums.ParseMode.HTML)


url = (
    "https://api.qrserver.com/v1/create-qr-code/?data="
    "{}&size=512x512&charset-source=UTF-8&charset-target=UTF-8&ecc=L&color=0-0-0&bgcolor=255-255-255&margin=1"
    "&qzone=1&format=png"
)
url2 = "https://api.qrserver.com/v1/read-qr-code/?outputformat=json"


@Client.on_message(filters.command("makeqr", prefix) & filters.me)
async def makeqrcode_handler(client: Client, message: Message):
    if len(message.text.split()) < 2:
        return await message.edit(
            f"Use: <code>{prefix}makeqr [text]</code>", parse_mode=enums.ParseMode.HTML
        )
    await message.edit("Generating qrcode...")
    data = message.text.split(maxsplit=1)[1]
    try:
        async with ClientSession() as session:
            async with session.get(url.format(data)) as response:
                qrcode = BytesIO(await response.read())
                qrcode.name = "qrcode.png"
                qrcode.seek(0)
                await message.reply_photo(qrcode)
                return await message.delete()
    except Exception as e:
        return await message.edit(
            f"<code>{format_exc(e)}</code>", parse_mode=enums.ParseMode.HTML
        )


modules_help["qrcode"] = {
    "read qr [photo or replay]": "Read qr code from photo or warm",
    "makeqr [text]": "Create qrcode from text",
}
