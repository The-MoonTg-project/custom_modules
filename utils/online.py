import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from datetime import datetime, timedelta
from utils.misc import modules_help, prefix
import re

online_task = None

def parse_time_duration(time_str):
    relative_pattern = r'^(\d+)(s|min|h|m)$'
    match = re.match(relative_pattern, time_str.lower())
    
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == 's':
            return value
        elif unit == 'min':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'm': # month
            return value * 30 * 24 * 3600
        
    absolute_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})$'
    match = re.match(absolute_pattern, time_str)
    
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        
        if hour >= 24:
            hour = 23
        if minute >= 60:
            minute = 59
            
        try:
            target_time = datetime(year, month, day, hour, minute)
            current_time = datetime.now()
            
            if target_time <= current_time:
                return None # Time has already passed
            
            delta = target_time - current_time
            return int(delta.total_seconds())
        except ValueError:
            return None
    
    return None

async def keep_online(duration):
    try:
        await asyncio.sleep(duration)
    except asyncio.CancelledError:
        pass

def format_time_remaining(seconds):
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours and {minutes} minutes"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} days and {hours} hours"

@Client.on_message(filters.command("onl", prefix) & filters.me)
async def online_keeper(client: Client, message: Message):
    global online_task
    
    if len(message.command) <= 1:
        if online_task and not online_task.done():
            await message.edit(
                "🟢 <b>Account is currently being kept online.</b>\n"
                "<i>Use the </i><code>/onl stop</code><i> command to stop.</i>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.edit(
                "🔴 <b>Account is not in auto-online mode.</b>\n"
                "<i>Example usage:</i>\n"
                "<code>/onl 30min</code> - for 30 minutes\n"
                "<code>/onl 2h</code> - for 2 hours\n"
                "<code>/onl 2025-12-31 23:59</code> - until a specific date",
                parse_mode=enums.ParseMode.HTML
            )
        return
    
    time_arg = " ".join(message.command[1:])
    
    if time_arg.lower() == "stop":
        if online_task and not online_task.done():
            online_task.cancel()
            await message.edit(
                "⏹️ <b>Online keeping has been stopped.</b>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.edit(
                "❌ <b>No online keeping process is active.</b>",
                parse_mode=enums.ParseMode.HTML
            )
        return
    
    duration = parse_time_duration(time_arg)
    
    if duration is None:
        await message.edit(
            "❌ <b>Invalid time format!</b>\n\n"
            "<i>Valid formats:</i>\n"
            "• <code>10s</code> - 10 seconds\n"
            "• <code>30min</code> - 30 minutes\n" 
            "• <code>2h</code> - 2 hours\n"
            "• <code>1m</code> - 1 month\n"
            "• <code>2025-12-31 23:59</code> - until a specific date\n"
            "• <code>stop</code> - to stop the process",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    max_duration = 30 * 24 * 3600 # 30 days
    if duration > max_duration:
        await message.edit(
            "⚠️ <b>The maximum allowed duration is 30 days.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    if online_task and not online_task.done():
        online_task.cancel()
    
    online_task = asyncio.create_task(keep_online(duration))
    
    time_formatted = format_time_remaining(duration)
    
    await message.edit(
        f"🟢 <b>Account will be kept online.</b>\n"
        f"⏱️ <b>Duration:</b> <code>{time_formatted}</code>\n"
        f"🔧 <b>Argument:</b> <code>{time_arg}</code>\n\n"
        f"<i>To stop:</i> <code>{prefix}onl stop</code>",
        parse_mode=enums.ParseMode.HTML
    )
    
    try:
        await online_task
        await client.send_message(
            message.chat.id,
            "⏰ <b>The online keeping period has ended.</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except asyncio.CancelledError:
        pass

modules_help["online_keeper"] = {
    "onl": "Display online status",
    "onl [time]*": "Keep account online for a specified duration.\n"
                   "Time formats:\n"
                   "• 10s - 10 seconds\n"
                   "• 30min - 30 minutes\n"
                   "• 2h - 2 hours\n"
                   "• 1m - 1 month\n"
                   "• 2025-12-31 23:59 - until a specific date",
    "onl stop": "Stop keeping the account online"
}
