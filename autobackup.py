from pyrogram import Client, filters, enums
from pyrogram.types import Message

from os import listdir

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix

# noinspection PyUnresolvedReferences
from utils.scripts import format_exc


@Client.on_message(filters.command(["lback"], prefix) & filters.me)
async def backup_database_cmd(_: Client, message: Message):
    """
    Backup the database.
    """
    if len(message.command) == 1:
        await message.edit("[😇] I think you didn't specify the name of the bot.")
        return
    await message.edit_text("<b>I'm copying the database...</b>", parse_mode=enums.ParseMode.HTML)
    try:
        name = message.command[1].lower()
        folders = listdir('/root/')
        if name not in folders:
            await message.edit("[😇] There is no such bot in the root folder.")
            return
        folder = listdir('/root/' + name)
        for file in folder:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                await message.reply_document(
                    document='/root/' + name + '/' + file,
                    caption='<code>Bot Database <b>' + name + '</b></code>',
                    parse_mode=enums.ParseMode.HTML
                )
                return await message.delete()
        folder = listdir('/root/' + name + '/assets')
        for file in folder:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                await message.reply_document(
                    document='/root/' + name + '/assets/' + file,
                    caption='<code>Bot Database <b>' + name + '</b></code>',
                    parse_mode=enums.ParseMode.HTML
                )
                return await message.delete()
        await message.edit("[😇] Database not found.")
    except Exception as ex:
        await message.edit_text(
            "Failed to back up the database!\n\n"
            f"{format_exc(ex)}",
            parse_mode=enums.ParseMode.HTML
        )


modules_help['autobackup'] = {
    'lback [name]*': '<b>Backup database from folder</b>',
    'lbackall': '<b>Backup all databases</b>'
}
