import asyncio
import logging

from pyrogram import Client, enums, filters
from pyrogram.errors import RPCError
from utils.misc import modules_help, prefix
from utils.scripts import text


# Helper function to get text from a message
def text(message):
    return message.reply_to_message.text if message.reply_to_message else ""


# Helper function to convert limit to an integer or None
def parse_limit(limit):
    return int(limit) if limit and limit.isdigit() else None


@Client.on_message(filters.command("shift", prefix) & filters.me)
async def shift(client, message):
    lol = await edit_or_reply(message, "Processing please wait")
    x = get_text(message)
    x = x.replace(" ", "")
    try:
        fromchat, tochat, limit, reverse = x.split("|")
        if reverse == "reverse":
            reverse = True
        else:
            reverse = False
    except:
        try:
            fromchat, tochat, limit = x.split("|")
            reverse = False
        except:
            await lol.edit("Check command syntax", parse_mode=enums.ParseMode.HTML)
    try:
        fromchat = int(fromchat)
    except:
        if not (fromchat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return
    try:
        tochat = int(tochat)
    except:
        if not (tochat.startswith("@")):
            await lol.edit("Enter a vailed username or id")
            return

    a = 0
    if limit == "None" or limit == "none":
        try:
            async for message in client.iter_history(fromchat, reverse=reverse):
                try:
                    await message.copy(tochat)
                    a = a + 1
                except Exception as e:
                    await lol.edit(e)
                    pass
                except RPCError as i:
                    await lol.edit(i)
                    pass

                await asyncio.sleep(1)
            await lol.edit(
                f"Successfully shifted {a} messages from {fromchat} to {tochat}"
            )
        except RPCError as i:
            await lol.edit(i)
            return
    else:
        try:
            limit = int(limit)
        except:
            lol.edit("Enter a vailed limit")
            return
        try:
            async for message in client.iter_history(
                fromchat, limit=limit, reverse=reverse
            ):
                try:
                    await message.copy(tochat)

                    a = a + 1
                except Exception as e:
                    await lol.edit(e)
                    pass
                except RPCError as i:
                    await lol.edit(i)
                    pass
                await asyncio.sleep(1)
            await lol.edit(
                f"Successfully shifted {a} messages from {fromchat} to {tochat}"
            )
        except RPCError as i:
            await lol.edit(i)
            return


@Client.on_message(filters.command("dmshift", prefix) & filters.me)
async def dmshift(client, message):
    await message.edit("Processing, please wait...")

    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.edit(
            "Invalid command format. Use: !dmshift @username_or_id",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    x = command_parts[1]

    if not message.reply_to_message:
        await message.edit("Reply to any message to deliver.")
        return

    reply = message.reply_to_message

    try:
        x = int(x)
    except ValueError:
        if not x.startswith("@"):
            await message.edit("Enter a valid username or ID.")
            return

    try:
        await reply.copy(chat_id=x)
    except Exception as e:
        await message.edit(f"Error: {str(e)}")
        return

    await message.edit(f"Message Delivered to {x}")


modules_help["shift"] = {
    "shift": "Steal all from one chat to other chat \n .shift fromchat | to chat | limit none for no limits\nNote: | is essential",
    "dmshift": "forward a message to someone without forward tag",
    "Special Thanks": "FridayUB",
}
