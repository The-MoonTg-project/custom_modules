import json

import requests

from pyrogram import Client, filters

from utils.misc import modules_help, prefix
from utils.scripts import format_small_module_help


@Client.on_message(filters.command(["trans", "tr"], prefix) & filters.me)
async def translatedl(_client, message):
    try:
        # Parse command arguments
        if len(message.command) > 1:
            dtarget = message.command[1]
        else:
            dtarget = "en"

        if len(message.command) > 2:
            dtext = message.text.split(None, 2)[2]
        elif message.reply_to_message:
            dtext = message.reply_to_message.text
        else:
            await message.edit_text(format_small_module_help("translator"))
            return

        await message.edit_text("<b>Translating</b>")

        # Use the Google Translate API endpoint
        url = "https://clients5.google.com/translate_a/t"
        params = {
            "client": "dict-chrome-ex",
            "sl": "auto",
            "tl": dtarget,
            "q": dtext
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            await message.edit_text(f"<b>Error:</b> API returned status code {response.status_code}")
            return

        # Parse the JSON response
        data = json.loads(response.text)

        # Based on actual response format [["translated_text", "detected_language"]]
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 0:
            translated_text = data[0][0]
            # Check if language detection is included
            source_lang = data[0][1] if len(data[0]) > 1 else "auto"
        else:
            translated_text = "Translation failed"
            source_lang = "unknown"

        await message.edit_text(
            f"<b>Translated</b> from <code>{
                source_lang}</code> to <code>{dtarget}</code>:\n\n"
            + "{}".format(translated_text)
        )

    except Exception as err:
        await message.edit_text(f"<b>Error:</b> <code>{str(err)}</code>")
        return


modules_help["translator"] = {
    "tr": "[lang] [text/reply] translate message",
    "trans": "[lang] [text/reply] translate message \n\nIf lang not given it'll use default(en)",
}
