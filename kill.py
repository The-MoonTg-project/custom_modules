from pyrogram import Client, filters
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from os import remove


@Client.on_message(filters.me & filters.command("killme", prefix))
async def killme_cmd(client, message: Message):
    await message.edit("Killing myself...")
    try:
        await client.stop()
        try:
            await client.disconnect()
        except:
            pass
        try:
            await client.session.close()
        except:
            pass
        os.remove("my_account.session")
    except:
        pass
    await message.edit("Killed myself! Closing session...")
