from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

commands = {
    'ftype': 'typing',
    'faudio': 'upload_audio',
    'fvideo': 'upload_video',
    'fphoto': 'upload_photo',
    'fdocument': 'upload_document',
    'flocation': 'find_location',
    'frvideo': 'record_video',
    'fvoice': 'record_audio',
    'frvideor': 'record_video_note',
    'fgame': 'playing',
    'fcontact': 'choose_contact',
    'fstop': 'cancel',
    'fscrn': 'screenshot'
}


# noinspection PyUnusedLocal
@Client.on_message(
    filters.command(list(commands), prefix) & filters.me
)
async def fakeactions_handler(client: Client, message: Message):
    cmd = message.command[0]
    try:
        sec = int(message.command[1])
        if sec > 60:
            sec = 60
    except:
        sec = None
    await message.delete()

    action = commands[cmd]

    try:
        if action != 'screenshot':
            if sec and action != 'cancel':
                await client.send_chat_action(chat_id=message.chat.id, action=action)
                await sleep(sec)
            else:
                return await client.send_chat_action(chat_id=message.chat.id, action=action)
        else:
            for _ in range(sec if sec else 1):
                await client.send(
                    functions.messages.SendScreenshotNotification(
                        peer=await client.resolve_peer(message.chat.id),
                        reply_to_msg_id=0,
                        random_id=client.rnd_id(),
                    )
                )
                await sleep(0.1)
    except Exception as e:
        return await client.send_message('me', f'Error in <b>fakeactions</b>'
                                               f' module:\n' + format_exc(e))


modules_help['fakeactions'] = {
    'ftype [sec]': 'Typing... action',
    'fvoice [sec]': 'Sending voice... action',
    'fvideo [sec]': 'Sending video... action',
    'fphoto [sec]': 'Sending photo... action',
    'fdocument [sec]': 'Sending document... action',
    'flocation [sec]': 'Find location... action',
    'fcontact [sec]': 'Sending contact... action',
    'frvideo [sec]': 'Recording video... action',
    'frvoice [sec]': 'Recording voice... action',
    'frvideor [sec]': 'Recording round video... action',
    'fgame [sec]': 'Playing game... action',
    'fstop': 'Stop actions',
    'fscrn [amount]': 'Make screenshot action',
}
