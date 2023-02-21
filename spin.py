import asyncio
import random
from io import BytesIO

import aiohttp

from pyrogram import Client, filters, types
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import import_library, format_exc, resize_image

# noinspection PyUnresolvedReferences
from modules.squotes import render_message

Image = import_library('PIL', 'pillow').Image
np = import_library('numpy')
imageio = import_library('imageio')


def create_gif(filename: str, offset: int, fps: int = 2, typ: str = 'spin'):
    img = Image.open(f'downloads/{filename}')
    if typ.lower() != 'spin':
        img = img.resize((random.randint(200, 1280), random.randint(200, 1280)), Image.ANTIALIAS)
    imageio.mimsave('downloads/video.gif', [img.rotate(-(i % 360)) for i in range(1, 361, offset)], fps=fps)


async def quote_cmd(client: Client, message: types.Message):
    count = 1

    is_png = False
    send_for_me = False
    no_reply = False

    messages = []

    async for msg in client.iter_history(
            message.chat.id, offset_id=message.reply_to_message.message_id, reverse=True
    ):
        if msg.empty:
            continue
        if msg.message_id >= message.message_id:
            break
        if no_reply:
            msg.reply_to_message = None

        messages.append(msg)

        if len(messages) >= count:
            break

    if send_for_me:
        await message.delete()
        message = await client.send_message("me", "<b>Generating...</b>")
    else:
        await message.edit("<b>Generating...</b>")

    url = "https://quotes.fl1yd.su/generate"
    params = {
        "messages": [
            await render_message(client, msg) for msg in messages if not msg.empty
        ],
        "quote_color": "#162330",
        "text_color": "#fff",
    }

    response = await aiohttp.ClientSession().post(url, json=params)
    if response.status != 200:
        return await message.edit(
            f"<b>Quotes API error!</b>\n" f"<code>{response.text}</code>"
        )

    resized = resize_image(
        BytesIO(await response.read()), img_type="PNG" if is_png else "WEBP"
    )
    return resized, is_png


@Client.on_message(filters.command(['spin', 'dspin'], prefix) & filters.me)
async def spin_handler(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit('<b>Reply to a <i>message</i> to spin it!</b>')
        return
    await message.edit('<b>Downloading sticker...</b>')
    try:
        coro = True
        if message.reply_to_message.document:
            filename = message.reply_to_message.document.file_name
            if not filename.endswith('.webp') and not filename.endswith('.png') and not filename.endswith('.jpg') \
                    and not filename.endswith('.jpeg'):
                return await message.edit('<b>Invalid file type!</b>')
        elif message.reply_to_message.sticker:
            if message.reply_to_message.sticker.is_video:
                return await message.edit('<b>Video stickers not allowed</b>')
            filename = 'sticker.webp'
        elif message.reply_to_message.text:
            result = await quote_cmd(client, message)
            if result[1]:
                filename = 'sticker.png'
            else:
                filename = 'sticker.webp'
            open(f'downloads/' + filename, 'wb').write(result[0].getbuffer())
            coro = False
        else:
            filename = 'photo.jpg'
        if coro:
            await message.reply_to_message.download(f'downloads/{filename}')
    except Exception as ex:
        return await message.edit(f'<b>Message can not be loaded:</b>\n<code>{format_exc(ex)}</code>')
    await message.edit('<b>Spinning...</b>')
    offset = int(message.command[1]) if len(message.command) > 1 else 10
    fps = int(message.command[2]) if len(message.command) > 2 else 30
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: create_gif(filename, offset, fps, message.command[0]))
        await message.delete()
        return await client.send_animation(chat_id=message.chat.id,
                                           animation='downloads/video.gif',
                                           reply_to_message_id=message.reply_to_message.message_id)
    except Exception as e:
        await message.reply(format_exc(e))


modules_help["spin"] = {
    "spin [offset] [fps]": "Spin message (Reply required)",
    "dspin [offset] [fps]": "SHAKAL spin message (Reply required)",
}
