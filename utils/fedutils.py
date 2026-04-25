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
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.db import db
from utils.scripts import format_exc
from utils import modules_help, prefix

# Global lock for fban tasks
FBAN_LOCK = asyncio.Lock()

# DB Keys
DB_MOD = "fedutils"
FED_DB_KEY = "FED_DB"
LOG_CH_KEY = "FBAN_LOG_CHANNEL"

# Broad success detection pattern
SUCCESS_PATTERN = (
    r"(FedBan|Fed Ban|Fed-Ban|Banned|Banning|unbanned|Un-FedBan|I'll give|has been|User banned|Done|"
    r"starting a federation ban|start a federation ban|FedBan reason updated|FedBan Reason update|"
    r"New FedBan|New un-FedBan|Would you like to update)"
)
SUCCESS_REGEX = re.compile(SUCCESS_PATTERN, re.IGNORECASE)

# Pattern to extract user name from bot response (e.g. "User: John Doe")
USER_NAME_REGEX = re.compile(r"User:\s*(.+)", re.IGNORECASE)


async def check_history_for_success(client: Client, chat_id: int, after_msg_id: int, tid):
    """Poll chat history for bot responses after our command.
    
    Returns (success: bool, extracted_name: str or None).
    Extracts user name from bot response for display purposes.
    """
    tid_str = str(tid)
    try:
        async for msg in client.get_chat_history(chat_id, limit=10):
            # Only look at messages that came after our command
            if msg.id <= after_msg_id:
                break
            
            # Skip our own messages
            if msg.from_user and msg.from_user.is_self:
                continue
            
            content = (msg.text or msg.caption or "")
            
            # Check: regex match OR target user ID in the text
            if SUCCESS_REGEX.search(content) or tid_str in content:
                # Handle Rose bot "Update reason" button
                if "Would you like to update this reason" in content and msg.reply_markup:
                    try:
                        await msg.click(0)
                    except Exception:
                        pass
                
                # Try to extract user name from bot response
                extracted_name = None
                name_match = USER_NAME_REGEX.search(content)
                if name_match:
                    extracted_name = name_match.group(1).strip()
                
                return True, extracted_name
    except Exception:
        pass
    return False, None


async def extract_target(client: Client, message: Message):
    """Helper to extract user information and reason."""
    args = message.text.split()
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        tid = target_user.id
        reason = " ".join(args[1:]) if len(args) > 1 else "None"
    else:
        if len(args) < 2: return None, None, None
        try:
            target_user = await client.get_users(args[1])
            tid = target_user.id
            reason = " ".join(args[2:]) if len(args) > 2 else "None"
        except Exception:
            try: tid = int(args[1])
            except ValueError: tid = args[1]
            target_user = None
            reason = " ".join(args[2:]) if len(args) > 2 else "None"
    
    if target_user:
        name = target_user.first_name + (f" {target_user.last_name}" if target_user.last_name else "")
        mention = f"<a href='tg://user?id={tid}'>{name}</a>"
    else:
        # Try resolving user info with integer ID as fallback
        try:
            resolved = await client.get_users(tid)
            name = resolved.first_name + (f" {resolved.last_name}" if resolved.last_name else "")
            mention = f"<a href='tg://user?id={tid}'>{name}</a>"
        except Exception:
            mention = f"<a href='tg://user?id={tid}'>{tid}</a>"
    return tid, mention, reason

async def run_fban_task(client: Client, message: Message, is_unban: bool = False):
    """Core fban/unfban logic using chat history polling for response detection."""
    tid, mention, reason = await extract_target(client, message)
    if not tid:
        return await message.edit("❌ <b>Reply to a user or provide an ID/Username.</b>")

    cmd_type = "unfban" if is_unban else "fban"
    act_name = "Un-FedBan" if is_unban else "FedBan"
    start_text = "Unban" if is_unban else "Ban"
    
    status_msg = await message.edit(f"<b>🌙 Starting Federation {start_text}...</b>")
    
    fed_db = db.get(DB_MOD, FED_DB_KEY, {})
    if not fed_db:
        return await status_msg.edit("❌ <b>No federations in database!</b>")

    log_ch = db.get(DB_MOD, LOG_CH_KEY)
    success_feds, failed_feds = [], []
    total = len(fed_db)

    async with FBAN_LOCK:
        extracted_user_name = None
        for cid_str, info in fed_db.items():
            cid = int(cid_str)
            custom_name = info.get("name", f"Fed({cid})")
            
            try:
                # Send command and record its message ID
                sent_cmd = await client.send_message(cid, f"/{cmd_type} {tid} {reason}")
                
                # Wait for the bot to process the command
                # Poll multiple times with increasing delay for reliability
                found = False
                for wait_secs in [3, 4, 5]:
                    await asyncio.sleep(wait_secs)
                    found, bot_name = await check_history_for_success(client, cid, sent_cmd.id, tid)
                    if found:
                        if bot_name and not extracted_user_name:
                            extracted_user_name = bot_name
                        break
                
                if found:
                    success_feds.append(custom_name)
                else:
                    failed_feds.append(custom_name)
            except Exception:
                failed_feds.append(custom_name)
            
            await asyncio.sleep(0.5)
    
    # Update mention with extracted name if we only had the ID
    if extracted_user_name:
        mention = f"<a href='tg://user?id={tid}'>{extracted_user_name}</a>"

    # Output formatting
    success_count = len(success_feds)
    failed_count = len(failed_feds)
    verb = "Unbanned" if is_unban else "Banned"
    header = "New Un-FedBan" if is_unban else "New FedBan"
    
    result_text = (
        f"<b>{header}</b>\n"
        f"<b>User:</b> {mention}\n"
        f"<b>User ID:</b> <code>{tid}</code>\n"
        f"<b>Reason:</b> {reason}\n"
        f"<b>{verb} in {success_count}/{total} feds</b>\n"
    )
    
    if failed_feds:
        for fname in failed_feds:
            result_text += f"• {fname}\n"
    
    result_text += "<b>#MoonUB</b>"

    await status_msg.edit(result_text, disable_web_page_preview=True)

    if log_ch:
        executor = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
        log_txt = f"#{cmd_type.upper()}\n\n"
        log_txt += f"<b>User:</b> {mention}\n"
        log_txt += f"<b>ID:</b> <code>{tid}</code>\n"
        log_txt += f"<b>Reason:</b> {reason}\n"
        log_txt += f"<b>Feds:</b> {success_count}/{total}\n"
        if success_feds:
            for sname in success_feds:
                log_txt += f"• {sname}\n"
        if failed_feds:
            log_txt += f"<b>Failed:</b> {failed_count}/{total}\n"
            for fname in failed_feds:
                log_txt += f"• {fname}\n"
        log_txt += f"\n<b>By:</b> {executor}"
        
        try: await client.send_message(log_ch, log_txt, disable_web_page_preview=True)
        except Exception: pass

@Client.on_message(filters.command("fban", prefix) & filters.me)
async def fban_handler(client, message):
    try: await run_fban_task(client, message, is_unban=False)
    except Exception as e: await message.edit(f"⚠️ <b>Error:</b> <code>{format_exc(e)}</code>")

@Client.on_message(filters.command("unfban", prefix) & filters.me)
async def unfban_handler(client, message):
    try: await run_fban_task(client, message, is_unban=True)
    except Exception as e: await message.edit(f"⚠️ <b>Error:</b> <code>{format_exc(e)}</code>")

@Client.on_message(filters.command("addfed", prefix) & filters.me)
async def addfed_handler(_, message: Message):
    if message.chat.type == "private":
        return await message.edit("❌ <b>Use in a group.</b>")
    args = message.text.split(maxsplit=1)
    custom_name = args[1] if len(args) > 1 else message.chat.title
    cid_str = str(message.chat.id)
    fed_db = db.get(DB_MOD, FED_DB_KEY, {})
    if cid_str in fed_db:
        return await message.edit("❌ <b>Already registered.</b>")
    fed_db[cid_str] = {"name": custom_name, "total_bots": 1}
    db.set(DB_MOD, FED_DB_KEY, fed_db)
    await message.edit(f"<b>Added {custom_name} to the list.</b>")

@Client.on_message(filters.command("delfed", prefix) & filters.me)
async def delfed_handler(_, message: Message):
    args = message.text.split()
    fed_db = db.get(DB_MOD, FED_DB_KEY, {})
    target = args[1] if len(args) > 1 else str(message.chat.id)
    if target not in fed_db:
        return await message.edit("❌ <b>Not found.</b>")
    name = fed_db.pop(target)["name"]
    db.set(DB_MOD, FED_DB_KEY, fed_db)
    await message.edit(f"<b>Removed {name} from the list.</b>")

@Client.on_message(filters.command("listfed", prefix) & filters.me)
async def listfed_handler(_, message: Message):
    fed_db = db.get(DB_MOD, FED_DB_KEY, {})
    if not fed_db: return await message.edit("❌ <b>No feds.</b>")
    text = "<b>📜 Federated Groups List:</b>\n\n"
    for fid, info in fed_db.items():
        text += f"• <b>{info['name']}</b> (<code>{fid}</code>)\n"
    await message.edit(text)

@Client.on_message(filters.command("setflog", prefix) & filters.me)
async def setflog_handler(_, message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.edit(f"❌ <b>Usage:</b> <code>{prefix}setflog [chat_id]</code>")
    try:
        log_id = int(args[1])
        db.set(DB_MOD, LOG_CH_KEY, log_id)
        await message.edit("<b>Added channel for fed logs.</b>")
    except ValueError: await message.edit("❌ <b>Invalid ID.</b>")

modules_help["fedutils"] = {
    "fban [reply]/[user]": "Sequentially ban in feds",
    "unfban [reply]/[user]": "Sequentially unban in feds",
    "addfed [name]": "Add current group to list",
    "delfed [id]": "Remove group from list",
    "listfed": "View registered federations",
    "setflog [id]": "Set logging channel",
}
