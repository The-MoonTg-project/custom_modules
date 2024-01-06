from utils.scripts import format_small_module_help, import_library
from utils.misc import modules_help, prefix
from pyrogram import Client, filters

googletrans = import_library("googletrans", "googletrans-py")
from googletrans import Translator

trl = Translator()

@Client.on_message(filters.command(["trans", "tr"], prefix) & filters.me)
async def translatedl(_client, message):
    dtarget = message.text.split(None, 2)[1]
    if len(message.command) > 2:
        dtext = message.text.split(None, 2)[2]
    elif message.reply_to_message:
        dtext = message.reply_to_message.text
    else:
        message.edit_text(format_small_module_help("translator"))
    try:
        message.edit_text(message.chat.id, "<b>Translating</b>")
        dtekstr = trl.translate(dtext, dest=dtarget)
    except ValueError as err:
        await message.edit("Error: <code>{}</code>".format(str(err)))
        return
    await message.edit("{}".format(dtekstr.text))


modules_help["translator"] = {
    "tr": "[lang]* [text/reply]* translate message",
    "trdl": f"[lang]* [your text]* short variant of {prefix}tr",
}
