from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import asyncio

@Client.on_message(filters.command("gcast") & filters.me)
async def gcast(client, message):
    if message.reply_to_message:
        msg = message.reply_to_message.text
    elif len(message.command) > 1:
        msg = " ".join(message.command[1:])
    else:
        await message.reply("Provide text or reply to a message to broadcast globally.")
        return

    await message.reply("Starting global broadcast...")
    done, errors = 0, 0

    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["supergroup", "group"]:
            try:
                await client.send_message(dialog.chat.id, msg)
                done += 1
            except FloodWait as e:
                await asyncio.sleep(e.value + 10)
            except Exception as e:
                errors += 1
                print(f"Error: {e}")

    await message.reply(f"Broadcast completed: {done} successful, {errors} failed.")

@Client.on_message(filters.command("gucast") & filters.me)
async def gucast(client, message):
    if message.reply_to_message:
        msg = message.reply_to_message.text
    elif len(message.command) > 1:
        msg = " ".join(message.command[1:])
    else:
        await message.reply("Provide text or reply to a message to broadcast globally to users.")
        return

    await message.reply("Starting global user broadcast...")
    done, errors = 0, 0

    async for dialog in client.get_dialogs():
        if dialog.chat.type == "private" and not dialog.chat.is_bot:
            try:
                await client.send_message(dialog.chat.id, msg)
                done += 1
            except Exception as e:
                errors += 1
                print(f"Error: {e}")

    await message.reply(f"Broadcast completed: {done} successful, {errors} failed.")
