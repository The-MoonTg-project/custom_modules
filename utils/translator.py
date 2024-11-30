# TODO
# WARNING! IT COMMENTED FULLY SINCE INSTALL PACKAGES FROM THIS MODULE WILL
# BROKE ALL FUCKING Moon, NOT JUST THIS MODULE
# THIS MODULE IS INCOMPATIBLE WITH LAST Moon VERSION
# SINCE IT USE OUTDATED PACKAGE WITH BROKEN DEPENDENCIES
# IT NEEDS TO BE REWRITEN

from utils.scripts import format_small_module_help, import_library
from utils.misc import modules_help, prefix
from pyrogram import Client, filters

googletrans = import_library("googletrans", "googletrans-py")
from googletrans import Translator

trl = Translator()


@Client.on_message(filters.command(["trans", "tr"], prefix) & filters.me)
async def translatedl(_client, message):
    try:
        if len(message.command) > 1:
            dtarget = message.text.split(None, 2)[1]
        else:
            dtarget = "en"
        if len(message.command) > 2:
            dtext = message.text.split(None, 2)[2]
        elif message.reply_to_message:
            dtext = message.reply_to_message.text
        else:
            message.edit_text(format_small_module_help("translator"))
        await message.edit_text("<b>Translating</b>")
        dtekstr = trl.translate(dtext, dest=dtarget)
        await message.edit_text(
            f"<b>Translated</b> to <code>{dtarget}</code> :\n\n"
            + "{}".format(dtekstr.text)
        )
    except ValueError as err:
        await message.edit("Error: <code>{}</code>".format(str(err)))
        return


modules_help["translator"] = {
    "tr": "[lang]* [text/reply]* translate message",
    "trans": "[lang]* [text/reply]* translate message \n If lang not given it'll use default(en)",
}
