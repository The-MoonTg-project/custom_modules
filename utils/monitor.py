from pyrogram import Client, filters, enums
from pyrogram.types import Message
import aiohttp
import asyncio
from typing import Dict, List
import time

from utils.misc import modules_help, prefix

# Dictionary to store active monitoring tasks
active_monitors: Dict[int, List[asyncio.Task]] = {}

async def ping_url(session: aiohttp.ClientSession, url: str, chat_id: int, client: Client):
    """Ping the URL and report results"""
    start_time = time.time()
    try:
        async with session.get(url) as response:
            latency = round((time.time() - start_time) * 1000, 2)
            status = response.status
            if status == 200:
                status_text = "🟢 UP"
            else:
                status_text = f"🟡 {status}"
    except Exception as e:
        latency = "N/A"
        status_text = f"🔴 DOWN ({str(e)})"
    
    await client.send_message(
        chat_id,
        f"<b>URL Monitor:</b> {url}\n"
        f"<b>Status:</b> {status_text}\n"
        f"<b>Latency:</b> {latency}ms\n"
        f"<b>Checked at:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode=enums.ParseMode.HTML
    )

async def monitor_task(url: str, interval: int, chat_id: int, client: Client):
    """Continuous monitoring task"""
    async with aiohttp.ClientSession() as session:
        while True:
            await ping_url(session, url, chat_id, client)
            await asyncio.sleep(interval * 60)  # Convert minutes to seconds

@Client.on_message(filters.command("monitor_start", prefix) & filters.me)
async def start_monitoring(client: Client, message: Message):
    """Start monitoring a URL"""
    if len(message.command) < 2:
        await message.edit(
            f"<b>Usage:</b> <code>{prefix}monitor_start [url] (interval)</code>\n\n"
            "<i>Default interval is 2 minutes</i>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    url = message.command[1]
    interval = 2  # Default 2 minutes
    
    if len(message.command) > 2:
        try:
            interval = int(message.command[2])
            if interval < 1:
                raise ValueError("Interval must be at least 1 minute")
        except ValueError:
            await message.edit(
                "<b>Invalid interval!</b> Please provide a number in minutes",
                parse_mode=enums.ParseMode.HTML
            )
            return
    
    user_id = message.from_user.id
    
    # Check if already monitoring this URL
    if user_id in active_monitors:
        for task in active_monitors[user_id]:
            if task.get_name() == f"monitor_{url}":
                await message.edit(
                    f"<b>Already monitoring this URL!</b>\n{url}",
                    parse_mode=enums.ParseMode.HTML
                )
                return
    
    # Create new monitoring task
    task = asyncio.create_task(
        monitor_task(url, interval, message.chat.id, client),
        name=f"monitor_{url}"
    )
    
    # Store the task
    if user_id not in active_monitors:
        active_monitors[user_id] = []
    active_monitors[user_id].append(task)
    
    await message.edit(
        f"<b>✅ Started monitoring:</b> {url}\n"
        f"<b>Interval:</b> Every {interval} minutes",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("monitor_stop", prefix) & filters.me)
async def stop_monitoring(client: Client, message: Message):
    """Stop monitoring a URL"""
    if len(message.command) < 2:
        await message.edit(
            f"<b>Usage:</b> <code>{prefix}monitor_stop [url|all]</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    user_id = message.from_user.id
    url_filter = message.command[1]
    
    if user_id not in active_monitors or not active_monitors[user_id]:
        await message.edit(
            "<b>No active monitors found!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    removed = 0
    
    if url_filter.lower() == "all":
        # Stop all monitors for this user
        for task in active_monitors[user_id]:
            task.cancel()
        removed = len(active_monitors[user_id])
        active_monitors[user_id] = []
    else:
        # Stop specific URL monitor
        new_tasks = []
        for task in active_monitors[user_id]:
            if task.get_name() == f"monitor_{url_filter}":
                task.cancel()
                removed += 1
            else:
                new_tasks.append(task)
        active_monitors[user_id] = new_tasks
    
    if removed > 0:
        await message.edit(
            f"<b>✅ Stopped {removed} monitor(s)</b>",
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.edit(
            f"<b>No matching monitors found for:</b> {url_filter}",
            parse_mode=enums.ParseMode.HTML
        )

@Client.on_message(filters.command("monitor_list", prefix) & filters.me)
async def list_monitors(client: Client, message: Message):
    """List active monitors"""
    user_id = message.from_user.id
    
    if user_id not in active_monitors or not active_monitors[user_id]:
        await message.edit(
            "<b>No active monitors!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    monitor_list = []
    for task in active_monitors[user_id]:
        if not task.done():
            monitor_list.append(
                f"• {task.get_name().replace('monitor_', '')}"
            )
    
    await message.edit(
        "<b>📋 Active Monitors:</b>\n" + "\n".join(monitor_list),
        parse_mode=enums.ParseMode.HTML
    )

modules_help["monitor"] = {
    "monitor_start [url] (interval)": "Start monitoring a URL (default: every 2 minutes)",
    "monitor_stop [url|all]": "Stop monitoring a specific URL or all monitors",
    "monitor_list": "List all active monitors",
}
