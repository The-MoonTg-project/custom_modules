from io import BytesIO
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


url = 'https://webshot.deam.io/{}/?width=1920&height=1080?type=jpg'


@Client.on_message(filters.command(["ws", "webshot"], prefix) & filters.me)
async def webshot_handler(client: Client, message: Message):
    try:
        await message.edit("<b>Screenshotting...</b>")
        link = message.command[1]
        async with ClientSession() as session:
            async with session.get(url.format(link)) as response:
                data = await response.read()
                file = BytesIO(data)
                file.name = 'screenshot.jpg'
                await message.delete()
                return await message.reply_photo(
                        photo=file,
                        caption=f"<b>Screenshot of</b> <code>{link}</code>"
                    )
    except Exception as e:
        await message.edit(format_exc(e))


modules_help['webshot'] = {
    'ws [site]*': 'Screenshot a website',
    'webshot [site]*': 'Screenshot a website',
}
