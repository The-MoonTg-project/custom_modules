import os

import shutil

from pyrogram import Client, filters
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, restart
from utils.db import db
from utils import config

if config.db_type in ["mongodb", "mongo"]:
    import bson


def dump_mongo(collections, path, db_):
    for coll in collections:
        with open(os.path.join(path, f"{coll}.bson"), "wb+") as f:
            for doc in db_[coll].find():
                f.write(bson.BSON.encode(doc))


def restore_mongo(path, db_):
    for coll in os.listdir(path):
        if coll.endswith(".bson"):
            with open(os.path.join(path, coll), "rb+") as f:
                db_[coll.split(".")[0]].insert_many(bson.decode_all(f.read()))


@Client.on_message(filters.command(["backup", "back"], prefix) & filters.me)
async def backup(client: Client, message: Message):
    """
    Backup the database
    """
    try:
        if not os.path.exists("backups/"):
            os.mkdir("backups/")

        await message.edit("<b>Backing up database...</b>")

        if config.db_type in ["mongo", "mongodb"]:
            dump_mongo(db._database.list_collection_names(), "backups/", db._database)
            return await message.edit(
                f"<b>Database backed up to:</b> <code>backups/</code> folder"
            )
        else:
            shutil.copy(config.db_name, f"backups/{config.db_name}")
            await client.send_document(
                "me",
                caption=f"<b>Database backup complete!\nType: </b>"
                f"<code>.restore</code> in response to this message to restore the database.",
                document=f"backups/{config.db_name}",
            )
            return await message.edit(
                "<b>Database backed up successfully! <code>(Check your favorites)</code></b>"
            )
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command(["restore", "res"], prefix) & filters.me)
async def restore(client: Client, message: Message):
    """
    Restore the database
    """
    try:
        await message.edit("<b>Restoring database...</b>")
        if config.db_type in ["mongo", "mongodb"]:
            restore_mongo("backups/", db._database)
            return await message.edit(
                f"<b>Database restored from:</b> <code>backups/</code> folder"
            )
        else:
            if not message.reply_to_message or not message.reply_to_message.document:
                return await message.edit(
                    "<b>Reply to a document to restore the database.</b>"
                )
            elif not message.reply_to_message.document.file_name.casefold().endswith(
                (".db", ".sqlite", ".sqlite3")
            ):
                return await message.edit(
                    "<b>Reply to a database file to restore the database.</b>"
                )
            await message.reply_to_message.download(
                f"backups/{message.reply_to_message.document.file_name}"
            )
            shutil.copy(
                f"backups/{message.reply_to_message.document.file_name}", config.db_name
            )
            await message.edit("<b>Database restored successfully!</b>")
            restart()
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command(["backupmods", "bms"], prefix) & filters.me)
async def backupmods(client: Client, message: Message):
    """
    Backup the modules
    """
    try:
        if not os.path.exists("backups/"):
            os.mkdir("backups/")

        await message.edit("<b>Backing up modules...</b>")

        from utils.misc import modules_help

        for mod in modules_help:
            if os.path.isfile(f"modules/custom_modules/{mod}.py"):
                f = open(f"backups/{mod}.py", "wb")
                f.write(open(f"modules/custom_modules/{mod}.py", "rb").read())
        await message.edit(
            text=f"<b>All modules backed up to:</b> <code>backups/</code> folder"
        )
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command(["backupmod", "bm"], prefix) & filters.me)
async def backupmod(client: Client, message: Message):
    """
    Backup the module
    """
    try:
        if not os.path.exists("backups/"):
            os.mkdir("backups/")
        from utils.misc import modules_help

        try:
            mod = message.text.split(maxsplit=1)[1].split(".")[0]
        except:
            return await message.edit(
                f"<b>Usage:</b> <code>{prefix}backupmod [module]</code>"
            )

        await message.edit("<b>Backing up module...</b>")

        if os.path.isfile(f"modules/custom_modules/{mod}.py"):
            f = open(f"backups/{mod}.py", "wb")
            f.write(open(f"modules/custom_modules/{mod}.py", "rb").read())
        else:
            return await message.edit(f"<b>Module <code>{mod}</code> not found.</b>")
        await message.reply_document(
            document=f"backups/{mod}.py",
            caption=f"<b>Module <code>{mod}</code> backed up to:</b> <code>backups/</code> folder",
        )
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command(["restoremod", "resmod"], prefix) & filters.me)
async def restoremod(client: Client, message: Message):
    """
    Restore the module
    """
    try:
        if not os.path.exists("backups/"):
            os.mkdir("backups/")
        from utils.misc import modules_help

        try:
            mod = message.text.split(maxsplit=1)[1].split(".")[0]
        except:
            return await message.edit(
                f"<b>Usage:</b> <code>{prefix}restoremod [module]</code>"
            )

        await message.edit("<b>Restoring module...</b>")

        if os.path.isfile(f"backups/{mod}.py"):
            f = open(f"modules/custom_modules/{mod}.py", "wb")
            f.write(open(f"backups/{mod}.py", "rb").read())
        else:
            return await message.edit(f"<b>Module <code>{mod}</code> not found.</b>")
        await message.edit(f"<b>Module <code>{mod}</code> restored successfully!</b>")
        restart()
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command(["restoremods", "resmods"], prefix) & filters.me)
async def restoremods(client: Client, message: Message):
    """
    Restore the modules
    """
    try:
        if not os.path.exists("backups/"):
            os.mkdir("backups/")

        await message.edit("<b>Restoring modules...</b>")

        for mod in os.listdir("backups/"):
            if mod.endswith(".py"):
                if os.path.isfile(f"modules/{mod}"):
                    continue
                f = open(f"modules/custom_modules/{mod}", "wb")
                f.write(open(f"backups/{mod}", "rb").read())
        await message.edit(
            text=f"<b>All modules restored from:</b> <code>backups/</code> folder"
        )
        restart()
    except Exception as e:
        await message.edit(format_exc(e))


modules_help["backup"] = {
    "backup": f"<b>Backup database</b>",
    "restore [reply]": f"<b>Restore database</b>",
    "backupmod [name]": f"<b>Backup mod</b>",
    "backupmods": f"<b>Backup all mods</b>",
    "resmod [name]": f"<b>Restore mod</b>",
    "resmods": f"<b>Restore all mods</b>",
}
