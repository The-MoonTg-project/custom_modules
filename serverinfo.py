from datetime import datetime
import os
import platform
import sys

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.enums.chat_type import ChatType
import requests

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix

# noinspection PyUnresolvedReferences
from utils.scripts import import_library


psutil = import_library("psutil")


def b2mb(b):
    return round(b / 1024 / 1024, 1)


def find_lib(lib: str) -> str:
    try:
        ver = (
            os.popen(f"python3 -m pip freeze | awk '/^{lib}==/'").read().split("==")[1]
        )
        if "\n" in ver:
            return ver.split("\n")[0]
        return ver
    except Exception:
        return "Not Installed"


def escape_html(txt: str) -> str:
    return txt.replace("<", "").replace(">", "")


text = (
    "<b><u>👾 Server Info:</u>\n\n"
    "<u>📅 System uptime:</u>\n"
    "    {} days, {} hours, {} minutes, {} seconds\n\n"
    "<u>🗄 Used resources:</u>\n"
    "    CPU: {} Cores {}%\n"
    "    RAM: {} / {}MB ({}%)\n"
    "    DISK: {} / {}MB ({}%)\n\n"
    "<u>🌐 Network Stats:</u>\n"
    "    Upload: {}MB\n"
    "    Download: {}MB\n"
    "    Total: {}MB\n"
    "    IPv4: <code>{}</code>\n\n"
    "<u>🧾 Dist info</u>\n"
    "    Kernel: {}\n    Arch: {}\n"
    "    OS: {}\n\n"
    "<u>📦 Python libs:</u>\n"
    "    Pyrogram: {}\n"
    "    Aiohttp: {}\n"
    "    GitPython: {}\n"
    "    Python: {}\n"
    "    Pip: {}</b>"
)


@Client.on_message(filters.command(["serverinfo", "sinfo"], prefix) & filters.me)
async def serverinfo_cmd(_: Client, message: Message):
    await message.edit(
        "<b>🔄 Getting server info...</b>", parse_mode=enums.ParseMode.HTML
    )

    inf = []

    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime = str(uptime).split(":")
        if len(uptime) == 3:
            inf.append("0")
            inf.append(uptime[0])
            inf.append(uptime[1])
            inf.append(uptime[2].split(".")[0])
        else:
            inf.append(uptime[0])
            inf.append(uptime[1])
            inf.append(uptime[2].split(".")[0])
            inf.append(uptime[3].split(".")[0])
    except Exception:
        uptime = "n/a"

    try:
        inf.append(psutil.cpu_count(logical=True))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(psutil.cpu_percent())
    except Exception:
        inf.append("n/a")

    try:
        inf.append(
            b2mb(psutil.virtual_memory().total - psutil.virtual_memory().available)
        )
    except Exception:
        inf.append("n/a")

    try:
        inf.append(b2mb(psutil.virtual_memory().total))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(psutil.virtual_memory().percent)
    except Exception:
        inf.append("n/a")

    try:
        inf.append(b2mb(psutil.disk_usage("/").used))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(b2mb(psutil.disk_usage("/").total))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(psutil.disk_usage("/").percent)
    except Exception:
        inf.append("n/a")

    try:
        download = 0
        upload = 0
        for net_io in psutil.net_io_counters(pernic=True).values():
            download += net_io.bytes_recv
            upload += net_io.bytes_sent
        inf.append(b2mb(upload))
        inf.append(b2mb(download))
        inf.append(b2mb(upload + download))
    except Exception:
        inf.append("n/a")

    try:
        if message.chat.type == enums.ChatType.PRIVATE:
            ip = requests.get("https://api.ipify.org?format=text").text
        else:
            ip = "***"
        inf.append(escape_html(ip))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(escape_html(platform.release()))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(escape_html(platform.architecture()[0]))
    except Exception:
        inf.append("n/a")

    try:
        t = platform.platform().split("-")
        android = t[2]
        if "android" in android:
            system = "Android (Termux)"
        else:
            system = os.popen("cat /etc/*release").read()
            b = system[system.find("PRETTY_NAME=") + 13 : -1]
            system = b[: b.find('"')]
        inf.append(escape_html(system))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(find_lib("pyrofork"))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(find_lib("aiohttp"))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(find_lib("GitPython"))
    except Exception:
        inf.append("n/a")

    try:
        inf.append(
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
    except Exception:
        inf.append("n/a")

    try:
        inf.append(os.popen("python3 -m pip --version").read().split()[1])
    except Exception:
        inf.append("n/a")

    await message.edit(text.format(*inf), parse_mode=enums.ParseMode.HTML)


modules_help["serverinfo"] = {
    "serverinfo": "Get server info ℹ️",
    "sinfo": "Get server info ℹ️",
}
