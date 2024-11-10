import os
import platform
import sys
import datetime
import psutil
import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix

# noinspection PyUnresolvedReferences
from utils.scripts import format_exc

def b2mb(b):
    return round(b / 1024 / 1024, 1)

def find_lib(lib: str) -> str:
    try:
        ver = os.popen(f"python3 -m pip freeze | awk '/^{lib}==/'").read().split("==")[1]
        if "\n" in ver:
            return ver.split("\n")[0]
        return ver
    except Exception:
        return "Not Installed"

def escape_html(txt: str) -> str:
    return txt.replace("<", "").replace(">", "")

# New function to get the OS distribution information
def get_os_info():
    try:
        with open("/etc/os-release") as f:
            info = {}
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    info[key] = value.strip('"')
            return f"{info.get('NAME')} {info.get('VERSION')} ({info.get('VERSION_CODENAME')})"
    except Exception:
        return "Unknown OS"

# New function to get the server's public IP address
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=text")
        return response.text
    except requests.RequestException:
        return "Unknown IP"

text = (
    "<b>👾 Server Information</b>\n\n"
    "<b>🗄 Resource Usage</b>\n"
    "- <b>CPU:</b> {} Cores ({}%)\n"
    "- <b>RAM:</b> {} / {} MB ({}%)\n"
    "- <b>Disk:</b> {} / {} MB ({}%)\n\n"
    "<b>📅 System Uptime</b>\n"
    "- <b>Uptime:</b> {}\n\n"
    "<b>🌐 Network Statistics</b>\n"
    "- <b>Sent:</b> {} MB\n"
    "- <b>Received:</b> {} MB\n"
    "- <b>IP:</b> {}\n\n"
    "<b>🧾 Operating System & Kernel</b>\n"
    "- <b>OS:</b> {}\n"
    "- <b>Kernel:</b> {}\n"
    "- <b>Arch:</b> {}\n\n"
    "<b>📦 Python Environment</b>\n"
    "- <b>Python:</b> {}\n"
    "- <b>Pip:</b> {}\n"
    "- <b>Libraries Installed:</b>\n"
    "  - <b>Pyrogram:</b> {}\n"
    "  - <b>Aiohttp:</b> {}\n"
    "  - <b>GitPython:</b> {}\n\n"
    "<b>👤 User Information</b>\n"
    "- <b>Current:</b> {}\n"
    "- <b>All:</b> {}\n"
)

@Client.on_message(filters.command(["server", "sinfo"], prefix) & filters.me)
async def serverinfo_cmd(_: Client, message: Message):
    await message.edit("<code>🔄 Collecting info...</code>", parse_mode=enums.ParseMode.HTML)

    inf = []
    try:
        inf.append(psutil.cpu_count(logical=True))
        inf.append(psutil.cpu_percent())
        inf.append(b2mb(psutil.virtual_memory().total - psutil.virtual_memory().available))
        inf.append(b2mb(psutil.virtual_memory().total))
        inf.append(psutil.virtual_memory().percent)
        inf.append(b2mb(psutil.disk_usage('/').used))
        inf.append(b2mb(psutil.disk_usage('/').total))
        inf.append(psutil.disk_usage('/').percent)

        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        inf.append(str(uptime).split('.')[0])  # Show uptime in HH:MM:SS

        inf.append(b2mb(psutil.net_io_counters().bytes_sent))
        inf.append(b2mb(psutil.net_io_counters().bytes_recv))

        # Get the public IP address
        inf.append(get_public_ip())

        # Use the new function to get OS information
        inf.append(get_os_info())
        inf.append(escape_html(platform.release()))
        inf.append(escape_html(platform.architecture()[0]))

        inf.append(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        inf.append(os.popen("python3 -m pip --version").read().split()[1])

        # Library versions
        inf.append(find_lib("pyrogram"))
        inf.append(find_lib("aiohttp"))
        inf.append(find_lib("GitPython"))

        # Alternative method to get the current user
        current_user = os.getenv("USER") or os.getenv("USERNAME") or "Unknown"
        inf.append(current_user)
        
        # Retrieve all logged-in users
        all_users = ", ".join([u.name for u in psutil.users()])
        inf.append(escape_html(all_users))

    except Exception as e:
        await message.edit(f"<b>Error:</b> {format_exc(e)}", parse_mode=enums.ParseMode.HTML)
        return

    await message.edit(text.format(*inf), parse_mode=enums.ParseMode.HTML)

modules_help["server"] = {
    "sinfo": "Get detailed server info.",
    "server": "Get detailed server info."
}
