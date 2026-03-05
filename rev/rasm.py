import json

import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.scripts import format_exc

from utils import modules_help, prefix

url = "https://armconverter.com/api/convert"
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain;charset=UTF-8",
    "dnt": "1",
    "origin": "https://armconverter.com",
    "priority": "u=1, i",
    "referer": "https://armconverter.com/",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}


@Client.on_message(filters.command("asm", prefix) & filters.me)
async def asm(_, message: Message):
    if len(message.command) > 1:
        asm_code = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text("Please provide an ASM code!")
        return

    try:
        await message.edit_text("<code>Processing...</code>")
        data = {
            "asm": f"{asm_code}",
            "offset": "",
            "arch": ["arm64", "arm", "armbe", "thumb", "thumbbe"],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                data=json.dumps(data),
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    result = ""
                    for arch, hex_data in response_data["hex"].items():
                        if hex_data[0]:
                            if hex_data[1] == "":
                                return await message.edit_text(
                                    "<b>ERROR:</b> <code>Invalid operand/mnemonic</code>"
                                )
                            result += f"{arch}: <code>{hex_data[1]}</code>\n"
                    if result == "":
                        await message.edit_text(
                            "<b>ERROR:</b> <code>Invalid operand/mnemonic</code>"
                        )
                    else:
                        await message.edit_text(
                            f"<b>INPUT:</b> <code>{asm_code}</code>\n<b>OUTPUT:</b> \n{result}"
                        )
                else:
                    await message.edit_text(
                        f"Request failed with status code {resp.status}"
                    )
    except Exception as e:
        await message.edit_text(format_exc(e))


@Client.on_message(filters.command("disasm", prefix) & filters.me)
async def disasm(_, message: Message):
    if len(message.command) > 1:
        hex_code = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text("Please provide a hex value!")
        return

    try:
        await message.edit_text("<code>Processing...</code>")
        data = {
            "hex": f"{hex_code}",
            "offset": "",
            "arch": ["arm64", "arm", "armbe", "thumb", "thumbbe"],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                data=json.dumps(data),
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    result = ""
                    for arch, asm_data in response_data["asm"].items():
                        if asm_data[0]:
                            result += f"{arch}: <code>{asm_data[1]}</code>\n"
                    if result == "":
                        await message.edit_text(
                            "<b>ERROR:</b> <code>Invalid operand/mnemonic</code>"
                        )
                    else:
                        await message.edit_text(
                            f"<b>INPUT:</b> <code>{hex_code}</code>\n</b>OUTPUT:</b> \n{result}"
                        )
                else:
                    await message.edit_text(
                        f"Request failed with status code {resp.status}"
                    )
    except Exception as e:
        await message.edit_text(format_exc(e))


modules_help["rasm"] = {
    "asm [asm code*]": "Convert an ASM code to ARM assembly hex code",
    "disasm [hex code*]": "Convert an ARM assembly hex code to ASM code",
}
