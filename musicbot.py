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

import os
import shutil
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import config

from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command("musicbot", prefix) & filters.me)
async def musicbot(client: Client, message: Message):
    user = await client.get_me()
    user_id = user.id
    allowed_handlers = [".", ",", "!", ";", "@"]
    if config.second_session == "":
        return await message.edit("<code>Second session string is not set.</code>")
    if config.music_handler == "":
        return await message.edit("<code>Music handler is not set.</code>")
    if config.music_handler not in allowed_handlers:
        return await message.edit("<code>Invalid music handler in config, please update.</code>")
    if config.music_handler == str(prefix):
        return await message.edit("<code>Music handler cannot be the same as main prefix.</code>")
    if shutil.which('termux-setup-storage'):
        return await message.edit("<code>Termux is not supported.</code>")

    try:
        await message.edit("Setting up musicbot")

        if os.path.exists("musicbot"):
            pass
        else:
            subprocess.run(["git", "clone", "https://github.com/The-MoonTg-project/musicbot.git"])

        with open("musicbot/config/config.py", "w") as f:
            f.write(f"API_ID: int = {config.api_id}\n")
            f.write(f"API_HASH: str = '{config.api_hash}'\n")
            f.write(f"SESSION_STRING: str = '{config.second_session}'\n")
            f.write(f"PREFIX: str = str('{config.music_handler}')\n")
            f.write("RPREFIX: str = str('$')\n")
            f.write(f"OWNER_ID: list[int] = [int('{user_id}')]\n")
            f.write("LOG_FILE_NAME: str = 'musicbot.txt'\n")

        subprocess.run(["pip", "install", "-r", "musicbot/requirements.txt"])
        await message.edit("Music bot setup completed.")

        if len(message.command) > 1 and message.command[1] == "on":
            music_bot_process = subprocess.Popen(["python", "-m", "YMusic"], cwd="musicbot")
            await message.edit("Music bot started in the background.")
        elif len(message.command) > 1 and message.command[1] == "off":
            music_bot_process.terminate()
            await message.edit("Music bot stopped.")

    except Exception as e:
        await message.edit(format_exc(e))


modules_help["musicbot"] = {
    "musicbot": "Setup music bot",
    "musicbot on": "Start the music bot in the background.",
    "musicbot off": "Stop the music bot running in the background.",
}
