from pyrogram import Client, filters
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# noinspection PyUnresolvedReferences
from utils.db import db


now_status = db.get('lordcodes.mafia', 'status', False)


async def status_filter(_, __, m):
    return now_status and m.chat.id == -1001169391811


status = filters.create(status_filter)


@Client.on_message(
    status
)
async def mafia_basic_lovler(client: Client, message: Message):
    try:
        if message.reply_markup and message.reply_markup.inline_keyboard:
            await message.click(0)
            return await client.send_message('me', '<b>🧛 MafiaDrawing:</b> gift successfully caught!')
    except Exception as e:
        return await client.send_message('me', f'<b>🧛 Mafia Drawing:</b>\n{format_exc(e)}')


# noinspection PyUnusedLocal
@Client.on_message(
    filters.command(["mafia", "md"], prefix) & filters.me
)
async def mafia_handler(client: Client, message: Message):
    global now_status
    now = not now_status
    db.set('lordcodes.mafia', 'status', now)
    now_status = now
    return await message.edit('<b><i>🧛 MafiaDrawing is now</i> ' + ('enabled</b>' if now else 'disabled</b>'))


modules_help['mafia'] = {
    'md': 'Enable/Disable Mafia Drawing',
}
