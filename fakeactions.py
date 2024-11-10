from asyncio import sleep
from pyrogram import Client, filters, enums
from pyrogram.raw import functions
from pyrogram.types import Message, InputReplyToMessage
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# Define the available actions with their corresponding chat actions
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

# Active action flag
active_action = False

@Client.on_message(filters.command(list(commands), prefix) & filters.me)
async def fakeactions_handler(client: Client, message: Message):
    global active_action  # Use the global flag to track ongoing actions
    
    cmd = message.command[0]
    action = commands.get(cmd)
    
    # Parse duration, defaulting to 1 second if not provided or invalid
    try:
        sec = int(message.command[1]) if len(message.command) > 1 else 1
    except ValueError:
        sec = 1  # Default to 1 second if an invalid duration is provided
    
    # Delete the original command message
    await message.delete()

    try:
        if cmd == 'fstop':  # Stop any ongoing action
            active_action = False  # Set flag to stop actions
            return  # Exit the function after stopping the action
        
        if action == 'screenshot':  # Special handling for screenshot action
            if message.reply_to_message:
                for _ in range(sec):
                    await client.invoke(
                        functions.messages.SendScreenshotNotification(
                            peer=await client.resolve_peer(message.chat.id),
                            reply_to=InputReplyToMessage(reply_to_message_id=message.reply_to_message.id),
                            random_id=client.rnd_id(),
                        )
                    )
                    await sleep(1)
            else:
                await client.send_message('me', "Error: 'fscrn' requires a reply to a message.")
        else:
            # Handle other chat actions for the specified duration
            active_action = True  # Set flag to indicate that an action is ongoing
            end_time = sec
            while end_time > 0 and active_action:  # Check if the action is still active
                await client.send_chat_action(chat_id=message.chat.id, action=action)
                await sleep(5)  # Resend every 5 seconds to maintain the action
                end_time -= 5
            active_action = False  # Reset the flag once the action completes
    except Exception as e:
        # Send any errors to the user's saved messages for debugging
        await client.send_message('me', f"Error in fakeactions module:\n{format_exc(e)}")

# Module help documentation for each command
modules_help['fakeactions'] = {
    'ftype [sec]': 'Typing... action',
    'faudio [sec]': 'Uploading audio... action',
    'fvideo [sec]': 'Uploading video... action',
    'fphoto [sec]': 'Uploading photo... action',
    'fdocument [sec]': 'Uploading document... action',
    'flocation [sec]': 'Finding location... action',
    'frvideo [sec]': 'Recording video... action',
    'frvoice [sec]': 'Recording voice... action',
    'frvideor [sec]': 'Recording round video... action',
    'fvideor [sec]': 'Uploading round video... action',
    'fgame [sec]': 'Playing game... action',
    'fcontact [sec]': 'Sending contact... action',
    'fstop': 'Stop any ongoing actions',
    'fscrn [sec] [reply_to_message]*': 'Simulate screenshot action (requires reply to a message)',
}
