from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.scripts import format_exc, import_library

from utils import modules_help, prefix

wikipedia = import_library("wikipedia")


@Client.on_message(filters.command("wiki", prefix) & filters.me)
async def wiki(_, message: Message):
    lang = message.command[1]
    user_request = " ".join(message.command[2:])
    if user_request == "":
        wikipedia.set_lang("en")
        user_request = " ".join(message.command[1:])
    try:
        if lang == "ru":
            wikipedia.set_lang("ru")

        result = wikipedia.summary(user_request)
        await message.edit(
            f"""<b>Request:</b>
<code>{user_request}</code>
<b>Result:</b>
<code>{result}</code>""",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)


modules_help["wikipedia"] = {
    "wiki [lang]* [request]*": "Search in RU/EN(default:en) Wikipedia",
}
