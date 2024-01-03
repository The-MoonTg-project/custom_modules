# This scripts contains use cases for userbots
# This is used on my Moon-Userbot: https://github.com/The-MoonTg-project/Moon-Userbot
# YOu can check it out for uses example
import os
import PIL.Image


from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library
from utils.config import gemini_key




@Client.on_message(filters.command("getai", prefix) & filters.me)
async def say(_, message: Message):
    await message.edit_text("<code>AI image assessment feature is temporarily disabled.</code>")


modules_help["aimage"] = {
    "getai [reply to image]*": "Get details of image with Ai",
}
