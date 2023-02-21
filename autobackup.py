from pyrogram import Client, filters
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
        await message.edit("[😇] Кажется ты не указал название бота.")
        return
    await message.edit_text("<b>Копирую базу данных...</b>")
    try:
        name = message.command[1].lower()
        folders = listdir('/root/')
        if name not in folders:
            await message.edit("[😇] Такого бота нет в root папке.")
            return
        folder = listdir('/root/' + name)
        for file in folder:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                await message.reply_document(
                    document='/root/' + name + '/' + file,
                    caption='<code>База данных бота <b>' + name + '</b></code>',
                )
                return await message.delete()
        folder = listdir('/root/' + name + '/assets')
        for file in folder:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                await message.reply_document(
                    document='/root/' + name + '/assets/' + file,
                    caption='<code>База данных бота <b>' + name + '</b></code>',
                )
                return await message.delete()
        await message.edit("[😇] База данных не найдена.")
    except Exception as ex:
        await message.edit_text(
            "Не удалось бэкапнуть базу данных!\n\n"
            f"{format_exc(ex)}"
        )


modules_help['autobackup'] = {
    'lback [name]*': '<b>Backup database from folder</b>',
    'lbackall': '<b>Backup all databases</b>'
}
