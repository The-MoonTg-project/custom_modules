from asyncio import sleep

from pyrogram import Client, filters, enums
from pyrogram.raw import functions
from pyrogram.types import Message, InputReplyToMessage
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

commands = {
    'ftype': enums.ChatAction.TYPING,
    'faudio': enums.ChatAction.UPLOAD_AUDIO,
    'fvideo': enums.ChatAction.UPLOAD_VIDEO,
    'fphoto': enums.ChatAction.UPLOAD_PHOTO,
    'fdocument': enums.ChatAction.UPLOAD_DOCUMENT,
    'flocation': enums.ChatAction.FIND_LOCATION,
    'frvideo': enums.ChatAction.RECORD_VIDEO,
    'frvoice': enums.ChatAction.RECORD_AUDIO,
    'frvideor': enums.ChatAction.RECORD_VIDEO_NOTE,
    'fvideor': enums.ChatAction.UPLOAD_VIDEO_NOTE,
    'fgame': enums.ChatAction.PLAYING,
    'fcontact': enums.ChatAction.CHOOSE_CONTACT,
    'fstop': enums.ChatAction.CANCEL,
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
            if sec and action != enums.ChatAction.CANCEL:
                await client.send_chat_action(chat_id=message.chat.id, action=action)
                await sleep(sec)
            else:
                return await client.send_chat_action(chat_id=message.chat.id, action=action)
        else:
            for _ in range(sec if sec else 1):
                await client.invoke(
                    functions.messages.SendScreenshotNotification(
                        peer=await client.resolve_peer(message.chat.id),
                        reply_to=InputReplyToMessage(reply_to_message_id=message.reply_to_message.id),
                        random_id=client.rnd_id(),
                    )
                )
                await sleep(0.1)
    except AttributeError:
        return await client.send_message('me', f'Error in <b>fakeactions</b>'
                                               'reply to message is required')
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
    'fvideor [sec]': 'Uploading round video... action',
    'fgame [sec]': 'Playing game... action',
    'fstop': 'Stop actions',
    'fscrn [amount] [reply_to_message]*': 'Make screenshot action',
}
