# XiaomiGeeks Plugin for Moon Userbot
# Provides various Xiaomi device information through @XiaomiGeeksBot

import asyncio
from pyrogram import Client, filters
from pyrogram.errors import UserBlocked
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


async def forward_xiaomi_bot_reply(client: Client, cmd_text: str, message: Message, loading_text: str):
    """Helper function to handle XiaomiGeeksBot interactions"""
    try:
        status_msg = await message.edit(loading_text)
        bot_username = "@XiaomiGeeksBot"

        # Send command to bot
        await client.send_message(bot_username, cmd_text)

        # Wait for response
        await asyncio.sleep(3)

        # Get and forward response
        async for msg in client.get_chat_history(bot_username, limit=1):
            await client.forward_messages(
                chat_id=message.chat.id,
                from_chat_id=bot_username,
                message_ids=msg.id
            )
            await status_msg.delete()
            return

        await status_msg.edit("<i>No response from bot.</i>")

    except UserBlocked:
        await message.edit("<i>Please unblock @XiaomiGeeksBot first.</i>")
    except Exception as e:
        await message.edit(f"<i>Error: {format_exc(e)}</i>")


@Client.on_message(filters.command("firmware", prefix) & filters.me)
async def firmware_cmd(client: Client, message: Message):
    """Get latest firmware for Xiaomi devices"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}firmware [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/firmware {message.command[1]}",
        message,
        "<i>Fetching firmware info...</i>"
    )


@Client.on_message(filters.command("vendor", prefix) & filters.me)
async def vendor_cmd(client: Client, message: Message):
    """Get latest vendor for Xiaomi devices"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}vendor [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/vendor {message.command[1]}",
        message,
        "<i>Fetching vendor info...</i>"
    )


@Client.on_message(filters.command("specs", prefix) & filters.me)
async def specs_cmd(client: Client, message: Message):
    """Get device specifications"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}specs [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/specs {message.command[1]}",
        message,
        "<i>Fetching device specs...</i>"
    )


@Client.on_message(filters.command("fastboot", prefix) & filters.me)
async def fastboot_cmd(client: Client, message: Message):
    """Get fastboot ROM"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}fastboot [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/fastboot {message.command[1]}",
        message,
        "<i>Fetching fastboot ROM...</i>"
    )


@Client.on_message(filters.command("recovery", prefix) & filters.me)
async def recovery_cmd(client: Client, message: Message):
    """Get recovery ROM"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}recovery [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/recovery {message.command[1]}",
        message,
        "<i>Fetching recovery ROM...</i>"
    )


@Client.on_message(filters.command("of", prefix) & filters.me)
async def of_cmd(client: Client, message: Message):
    """Get OrangeFox Recovery"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}of [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/of {message.command[1]}",
        message,
        "<i>Fetching OrangeFox Recovery...</i>"
    )


@Client.on_message(filters.command("latest", prefix) & filters.me)
async def latest_cmd(client: Client, message: Message):
    """Get latest OS versions info"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}latest [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/latest {message.command[1]}",
        message,
        "<i>Fetching latest OS info...</i>"
    )


@Client.on_message(filters.command("archive", prefix) & filters.me)
async def archive_cmd(client: Client, message: Message):
    """Get official ROM archive links"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}archive [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/archive {message.command[1]}",
        message,
        "<i>Fetching archive links...</i>"
    )


@Client.on_message(filters.command("eu", prefix) & filters.me)
async def eu_cmd(client: Client, message: Message):
    """Get Xiaomi.eu ROMs"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}eu [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/eu {message.command[1]}",
        message,
        "<i>Fetching Xiaomi.eu ROMs...</i>"
    )


@Client.on_message(filters.command("twrp", prefix) & filters.me)
async def twrp_cmd(client: Client, message: Message):
    """Get TWRP download link"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}twrp [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/twrp {message.command[1]}",
        message,
        "<i>Fetching TWRP...</i>"
    )


@Client.on_message(filters.command("models", prefix) & filters.me)
async def models_cmd(client: Client, message: Message):
    """Get available device models"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}models [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/models {message.command[1]}",
        message,
        "<i>Fetching models...</i>"
    )


@Client.on_message(filters.command("whatis", prefix) & filters.me)
async def whatis_cmd(client: Client, message: Message):
    """Get device name from codename"""
    if len(message.command) < 2:
        await message.edit(f"<b>Usage:</b> <code>{prefix}whatis [codename]</code>")
        return
    await forward_xiaomi_bot_reply(
        client,
        f"/whatis {message.command[1]}",
        message,
        "<i>Identifying device...</i>"
    )


modules_help["xiaomi"] = {
    "archive [codename]": "Get official ROM archive links",
    "eu [codename]": "Get Xiaomi.eu ROMs",
    "fastboot [codename]": "Get fastboot ROM",
    "firmware [codename]": "Get latest firmware for Xiaomi device",
    "latest [codename]": "Get latest OS versions info",
    "models [codename]": "Get available device models",
    "of [codename]": "Get OrangeFox Recovery",
    "recovery [codename]": "Get recovery ROM",
    "specs [codename]": "Get device specifications",
    "twrp [codename]": "Get TWRP download link",
    "vendor [codename]": "Get latest vendor for Xiaomi device",
    "whatis [codename]": "Get device name from codename"
}