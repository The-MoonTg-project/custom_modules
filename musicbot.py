# Moon-Userbot - telegram userbot
# Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import os
import shutil
import subprocess
import sys
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import config

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, run_cmd, import_library
from utils.db import db

import_library("psutil")
import psutil


ALLOWED_HANDLERS = [".", ",", "!", ";", "@", "#"]


@Client.on_message(filters.command("musicbot", prefix) & filters.me)
async def musicbot(client: Client, message: Message):
    user = await client.get_me()
    user_id = user.id
    music_handler = db.get("custom.musicbot", "music_handler", "")
    if config.second_session == "":
        return await message.edit("<code>Second session string is not set.</code>")
    if music_handler == "":
        return await message.edit(
            "<b>Music handler is not set.</b>\nYou can set it using <code>.set_mhandler [your handler]</code> command.\nAllowed handlers are <code>. , ! ; @ #</code>"
        )
    if music_handler not in ALLOWED_HANDLERS:
        return await message.edit(
            "<code>Invalid music handler in config, please update.</code>"
        )
    if music_handler == str(prefix):
        return await message.edit(
            "<code>Music handler cannot be the same as main prefix.</code>"
        )
    if shutil.which("termux-setup-storage"):
        return await message.edit("<code>Termux is not supported.</code>")

    try:
        await message.edit("<code>Processing...</code>")
        if (
            not os.path.exists("musicbot")
            or len(message.command) > 1
            and message.command[1] == "re"
        ):
            await message.edit("Setting up music bot...")
            if os.path.exists("musicbot"):
                shutil.rmtree("musicbot")
            subprocess.run(
                ["git", "clone", "https://github.com/The-MoonTg-project/musicbot.git"]
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements.txt",
                ],
                cwd="musicbot",
            )
            with open("musicbot/config/config.py", "w") as f:
                f.write(f"API_ID: int = {config.api_id}\n")
                f.write(f"API_HASH: str = '{config.api_hash}'\n")
                f.write(f"SESSION_STRING: str = '{config.second_session}'\n")
                f.write(f"PREFIX: str = str('{music_handler}')\n")
                f.write("RPREFIX: str = str('$')\n")
                f.write(f"OWNER_ID: list[int] = [int('{user_id}')]\n")
                f.write("LOG_FILE_NAME: str = 'musicbot.txt'\n")
            return await message.edit("Music bot setup completed.")

        if len(message.command) == 1:
            return await message.edit("Music bot is already set up.")

        if len(message.command) > 1 and message.command[1] in ["on", "start"]:
            music_bot_pid = db.get("custom.musicbot", "music_bot_pid", None)
            if music_bot_pid is None:
                await message.edit("Starting music bot...")
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        "requirements.txt",
                    ],
                    cwd="musicbot",
                )
                music_bot_process = subprocess.Popen(
                    [sys.executable, "-m", "YMusic"], cwd="musicbot"
                )
                await asyncio.sleep(3)
                db.set("custom.musicbot", "music_bot_pid", music_bot_process.pid)
                return await message.edit("Music bot started in the background.")
            return await message.edit("Music bot is already running.")
        elif len(message.command) > 1 and message.command[1] in ["off", "stop"]:
            music_bot_pid = db.get("custom.musicbot", "music_bot_pid", None)
            if music_bot_pid is None:
                return await message.edit(
                    "Music bot is not running. Please turn on musicbot first."
                )
            try:
                music_bot_process = psutil.Process(music_bot_pid)
                music_bot_process.terminate()
                db.remove("custom.musicbot", "music_bot_pid")
            except psutil.NoSuchProcess:
                db.remove("custom.musicbot", "music_bot_pid")
                return await message.edit(
                    "Music bot is not running. Please turn on musicbot first."
                )
            db.remove("custom.musicbot", "music_bot_pid")
            return await message.edit("Music bot stopped.")
        elif len(message.command) > 1 and message.command[1] == "restart":
            music_bot_pid = db.get("custom.musicbot", "music_bot_pid", None)
            if music_bot_pid is None:
                return await message.edit(
                    "Music bot is not running. Please turn on musicbot first."
                )
            try:
                music_bot_process = psutil.Process(music_bot_pid)
                music_bot_process.terminate()
            except psutil.NoSuchProcess:
                pass
            music_bot_process = subprocess.Popen(
                [sys.executable, "-m", "YMusic"], cwd="musicbot"
            )
            await asyncio.sleep(3)
            db.set("custom.musicbot", "music_bot_pid", music_bot_process.pid)
            return await message.edit("Music bot restarted in the background.")
    except Exception as e:
        return await message.edit(format_exc(e))


@Client.on_message(filters.command("set_mhandler", prefix) & filters.me)
async def set_mhandler(_, message: Message):
    if len(message.command) < 2:
        return await message.edit("Please provide a new music handler.")
    new_handler = message.command[1]
    if new_handler not in ALLOWED_HANDLERS:
        return await message.edit(
            "Invalid music handler provided! \n Allowed handlers: <code>.</code> <code>,</code> <code>!</code> <code>;</code> <code>@</code> <code>#</code>"
        )
    db.set("custom.musicbot", "music_handler", new_handler)
    return await message.edit(f"Music handler set to {new_handler}")


modules_help["musicbot"] = {
    "musicbot": "Setup music bot",
    "musicbot [on|start]": "Start the music bot in the background.",
    "musicbot [off|stop]": "Stop the music bot running in the background.",
    "musicbot restart": "Restart the music bot in the background.",
    "musicbot re": "Update the music bot code and restart it.",
    "set_mhandler": "Set the music handler for the bot.",
}
