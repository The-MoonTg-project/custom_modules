#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.db import db
from utils.scripts import format_exc
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("fban", prefix) & filters.me)
async def fban_cmd(client: Client, message: Message):
    try:
        msg = await message.edit("🌙 Starting Federation Ban...")
        
        # Get target and reason
        args = message.text.split()
        if len(args) < 2 and not message.reply_to_message:
            return await msg.edit("❌ Reply to user or provide ID/username and reason")
        
        if message.reply_to_message:
            target = message.reply_to_message.from_user.id
            reason = " ".join(args[1:]) if len(args) > 1 else ""
        else:
            target = args[1]
            reason = " ".join(args[2:]) if len(args) > 2 else ""

        # Get configuration
        fban_group = db.get("core.ats", "FBAN_GROUP_ID")
        fed_ids = db.get("core.ats", "FED_IDS", [])
        
        if not fban_group:
            return await msg.edit("❌ FBAN group not set! Use `.set_fban_group` first")
        
        if not fed_ids:
            return await msg.edit("❌ No federations added! Use `.addfed` first")

        # Execute commands in FBAN group
        await client.send_message(fban_group, f"/fban {target} {reason}")
        await asyncio.sleep(2)
        
        for fed_id in fed_ids:
            await client.send_message(fban_group, f"/joinfed {fed_id}")
            await asyncio.sleep(3)
            await client.send_message(fban_group, f"/fban {target} {reason}")
            await asyncio.sleep(3)

        await msg.edit(f"✅ Successfully FBanned {target} in {len(fed_ids)} federations\n#MoonUB")

    except Exception as e:
        await msg.edit(f"⚠️ Error: {format_exc(e)}")

@Client.on_message(filters.command("unfban", prefix) & filters.me)
async def unfban_cmd(client: Client, message: Message):
    try:
        msg = await message.edit("🌙 Starting Federation Unban...")
        
        # Get target and reason
        args = message.text.split()
        if len(args) < 2 and not message.reply_to_message:
            return await msg.edit("❌ Reply to user or provide ID/username and reason")
        
        if message.reply_to_message:
            target = message.reply_to_message.from_user.id
            reason = " ".join(args[1:]) if len(args) > 1 else ""
        else:
            target = args[1]
            reason = " ".join(args[2:]) if len(args) > 2 else ""

        # Get configuration
        fban_group = db.get("core.ats", "FBAN_GROUP_ID")
        fed_ids = db.get("core.ats", "FED_IDS", [])
        
        if not fban_group:
            return await msg.edit("❌ FBAN group not set! Use `.set_fban_group` first")
        
        if not fed_ids:
            return await msg.edit("❌ No federations added! Use `.addfed` first")

        # Execute commands in FBAN group
        await client.send_message(fban_group, f"/unfban {target} {reason}")
        await asyncio.sleep(2)
        
        for fed_id in fed_ids:
            await client.send_message(fban_group, f"/joinfed {fed_id}")
            await asyncio.sleep(3)
            await client.send_message(fban_group, f"/unfban {target} {reason}")
            await asyncio.sleep(3)

        await msg.edit(f"✅ Successfully UnFBanned {target} in {len(fed_ids)} federations\n#MoonUB")

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
    await message.edit(f"📜 Federation List:\n{fed_list}")

modules_help["fedutils"] = {
    "fban [reply]/[userid]* [reason]": "Ban user in multiple federations",
    "unfban [reply]/[userid]* [reason]": "Unban user from multiple federations",
    "set_fban_group [group_id]*": "Set group for FBAN operations",
    "addfed [fed_id]*": "Add federation to ban list",
    "delfed [fed_id]*": "Remove federation from ban list",
    "listfed": "Show current federation list"
}