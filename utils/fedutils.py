import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.db import db
from utils.scripts import format_exc
from utils.misc import modules_help, prefix


@Client.on_message(filters.command("fban", prefix) & filters.me)
async def fban_cmd(client: Client, message: Message):
    try:
        msg = await message.edit("<b>🌙 Starting Federation Ban...</b>")
        
        args = message.text.split()
        if len(args) < 2 and not message.reply_to_message:
            return await msg.edit("❌ Reply to user or provide ID/username and reason")
        
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            target = target_user.id
            reason = " ".join(args[1:]) if len(args) > 1 else ""
        else:
            try:
                target_user = await client.get_users(args[1])
                target = target_user.id
                reason = " ".join(args[2:]) if len(args) > 2 else ""
            except Exception:
                target = args[1]
                target_user = None
                reason = " ".join(args[2:]) if len(args) > 2 else ""

        fban_group = db.get("core.ats", "FBAN_GROUP_ID")
        fed_ids = db.get("core.ats", "FED_IDS", [])

        if not fban_group:
            return await msg.edit("❌ FBAN group not set! Use `.set_fban_group` first")

        if not fed_ids:
            return await msg.edit("❌ No federations added! Use `.addfed` first")

        await client.send_message(fban_group, f"/fban {target} {reason}")
        await asyncio.sleep(2)

        for fed_id in fed_ids:
            await client.send_message(fban_group, f"/joinfed {fed_id}")
            await asyncio.sleep(3)
            await client.send_message(fban_group, f"/fban {target} {reason}")
            await asyncio.sleep(3)

        # Fetch user info for mention
        try:
            if not target_user:
                target_user = await client.get_users(target)

            user_name = target_user.first_name
            if target_user.last_name:
                user_name += f" {target_user.last_name}"
            user_mention = f"<a href='tg://user?id={target_user.id}'>{user_name}</a>"
            user_id_display = str(target_user.id)
        except Exception:
            user_mention = str(target)
            user_id_display = str(target)

        result_message = (
            f"<b>New FedBan</b>\n"
            f"<b>Fed:</b> Fbanned in {len(fed_ids)} feds\n"
            f"<b>User:</b> {user_mention}\n"
            f"<b>User ID:</b> {user_id_display}\n"
            f"<b>Reason:</b> {reason if reason else 'Not specified'}\n"
            f"#MoonUB"
        )

        await msg.edit(result_message, disable_web_page_preview=True)

    except Exception as e:
        await msg.edit(f"⚠️ Error: {format_exc(e)}")


@Client.on_message(filters.command("unfban", prefix) & filters.me)
async def unfban_cmd(client: Client, message: Message):
    try:
        msg = await message.edit("<b>🌙 Starting Federation Unban...</b>")
        
        args = message.text.split()
        if len(args) < 2 and not message.reply_to_message:
            return await msg.edit("❌ Reply to user or provide ID/username and reason")

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            target = target_user.id
            reason = " ".join(args[1:]) if len(args) > 1 else ""
        else:
            try:
                target_user = await client.get_users(args[1])
                target = target_user.id
                reason = " ".join(args[2:]) if len(args) > 2 else ""
            except Exception:
                target = args[1]
                target_user = None
                reason = " ".join(args[2:]) if len(args) > 2 else ""

        fban_group = db.get("core.ats", "FBAN_GROUP_ID")
        fed_ids = db.get("core.ats", "FED_IDS", [])

        if not fban_group:
            return await msg.edit("❌ FBAN group not set! Use `.set_fban_group` first")

        if not fed_ids:
            return await msg.edit("❌ No federations added! Use `.addfed` first")

        await client.send_message(fban_group, f"/unfban {target} {reason}")
        await asyncio.sleep(2)

        for fed_id in fed_ids:
            await client.send_message(fban_group, f"/joinfed {fed_id}")
            await asyncio.sleep(3)
            await client.send_message(fban_group, f"/unfban {target} {reason}")
            await asyncio.sleep(3)

        # Fetch user info for mention
        try:
            if not target_user:
                target_user = await client.get_users(target)

            user_name = target_user.first_name
            if target_user.last_name:
                user_name += f" {target_user.last_name}"
            user_mention = f"<a href='tg://user?id={target_user.id}'>{user_name}</a>"
            user_id_display = str(target_user.id)
        except Exception:
            user_mention = str(target)
            user_id_display = str(target)

        result_message = (
            f"<b>New FedUnban</b>\n"
            f"<b>Fed:</b> Unbanned in {len(fed_ids)} feds\n"
            f"<b>User:</b> {user_mention}\n"
            f"<b>User ID:</b> {user_id_display}\n"
            f"<b>Reason:</b> {reason if reason else 'Not specified'}\n"
            f"#MoonUB"
        )

        await msg.edit(result_message, disable_web_page_preview=True)

    except Exception as e:
        await msg.edit(f"⚠️ Error: {format_exc(e)}")


@Client.on_message(filters.command("set_fban_group", prefix) & filters.me)
async def set_fban_group(_, message: Message):
    if len(message.command) < 2:
        return await message.edit(f"❌ Usage: `{prefix}set_fban_group <group_id>`")
    
    try:
        group_id = int(message.command[1])
        db.set("core.ats", "FBAN_GROUP_ID", group_id)
        await message.edit(f"✅ FBAN group set to `{group_id}`")
    except ValueError:
        await message.edit("❌ Invalid group ID. Must be a valid integer.")
    except Exception as e:
        await message.edit(f"⚠️ Error: {format_exc(e)}")


@Client.on_message(filters.command("addfed", prefix) & filters.me)
async def add_fed(_, message: Message):
    if len(message.command) < 2:
        return await message.edit(f"❌ Usage: `{prefix}addfed <fed_id>`")
    
    fed_id = message.command[1]
    current_feds = db.get("core.ats", "FED_IDS", [])
    
    if fed_id in current_feds:
        await message.edit("❌ This federation is already in the list")
    else:
        current_feds.append(fed_id)
        db.set("core.ats", "FED_IDS", current_feds)
        await message.edit(f"✅ Added federation: `{fed_id}`")


@Client.on_message(filters.command("delfed", prefix) & filters.me)
async def del_fed(_, message: Message):
    if len(message.command) < 2:
        return await message.edit(f"❌ Usage: `{prefix}delfed <fed_id>`")
    
    fed_id = message.command[1]
    current_feds = db.get("core.ats", "FED_IDS", [])
    
    if fed_id not in current_feds:
        await message.edit("❌ Federation not found in list")
    else:
        current_feds.remove(fed_id)
        db.set("core.ats", "FED_IDS", current_feds)
        await message.edit(f"✅ Removed federation: `{fed_id}`")


@Client.on_message(filters.command("listfed", prefix) & filters.me)
async def list_fed(_, message: Message):
    current_feds = db.get("core.ats", "FED_IDS", [])
    if not current_feds:
        return await message.edit("❌ No federations in list")
    
    fed_list = "\n".join([f"• `{fed}`" for fed in current_feds])
    await message.edit(f"<b>📜 Federation List:</b>\n{fed_list}")


modules_help["fedutils"] = {
    "fban [reply]/[userid]* [reason]": "Ban user in multiple federations",
    "unfban [reply]/[userid]* [reason]": "Unban user from multiple federations",
    "set_fban_group [group_id]*": "Set group for FBAN operations",
    "addfed [fed_id]*": "Add federation to ban list",
    "delfed [fed_id]*": "Remove federation from ban list",
    "listfed": "Show current federation list"
}
