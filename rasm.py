import json

import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# Define the URL and headers
url = "https://armconverter.com/api/convert"
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'text/plain;charset=UTF-8',
    'dnt': '1',
    'origin': 'https://armconverter.com',
    'priority': 'u=1, i',
    'referer': 'https://armconverter.com/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
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
        # Define the data to be sent
        data = {
            "asm": f"{asm_code}",
            "offset": "",
            "arch": ["arm64","arm","armbe","thumb","thumbbe"]
        }

        # Send the request
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            result = ""
            for arch, hex_data in response_data["hex"].items():
                if hex_data[0]:
                    result += f"{arch}: {hex_data[1]}\n"
            if result == "":
                await message.edit_text("<b>ERROR:</b> <code>Invalid mnemonic</code>")
            else:
                await message.edit_text(f"<b>INPUT:</b> <code>{asm_code}</code>\n<b>OUTPUT:</b> \n<code>{result}</code>")
        else:
            await message.edit_text(
                f"Request failed with status code {response.status_code}"
            )
    except Exception as e:
        await message.edit_text(format_exc(e))

@Client.on_message(filters.command("disasm", prefix) & filters.me)
async def disasm(_, message: Message):

    if len(message.command) > 1:
        hex_code = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text("Please provide an ASM code!")
        return

    try:
        await message.edit_text("<code>Processing...</code>")
        # Define the data to be sent
        data = {
            "hex": f"{hex_code}",
            "offset": "",
            "arch": ["arm64","arm","armbe","thumb","thumbbe"]
        }

        # Send the request
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            result = ""
            for arch, asm_data in response_data["asm"].items():
                if asm_data[0]:
                    result += f"{arch}: {asm_data[1]}\n"
                    result += f"{arch}: {asm_data[1]}\n"
            if result == "":
                await message.edit_text("<b>ERROR:</b> <code>Invalid mnemonic</code>")
            else:
                await message.edit_text(f"<b>INPUT:</b> <code>{hex_code}</code>\n</b>OUTPUT:</b> \n<code>{result}</code>")
        else:
            await message.edit_text(
                f"Request failed with status code {response.status_code}"
            )
    except Exception as e:
        await message.edit_text(format_exc(e))

modules_help["rasm"] = {
    "asm [asm code*]": "Convert an ASM code to ARM assembly hex code",
    "disasm [hex code*]": "Convert an ARM assembly hex code to ASM code"
}
