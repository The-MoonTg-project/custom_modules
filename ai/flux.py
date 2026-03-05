import io
import os
import time

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.scripts import format_exc, progress

from utils import modules_help, prefix


async def schellwithflux(args):
    API_URL = "https://randydev-ryuzaki-api.hf.space/api/v1/akeno/fluxai"
    payload = {"user_id": 1191668125, "args": args}  # Please don't edit here
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload) as resp:
            if resp.status != 200:
                print(f"Error status {resp.status}")
                return None
            return await resp.read()


@Client.on_message(filters.command("fluxai", prefix) & filters.me)
async def imgfluxai_(client: Client, message: Message):
    question = message.text.split(" ", 1)[1] if len(message.command) > 1 else None
    if not question:
        return await message.reply_text("Please provide a question for Flux.")
    try:
        image_bytes = await schellwithflux(question)
        if image_bytes is None:
            return await message.reply_text("Failed to generate an image.")
        pro = await message.reply_text("Generating image, please wait...")

        # Write the image bytes directly to a file
        with open("flux_gen.jpg", "wb") as f:
            f.write(image_bytes)

        ok = await pro.edit_text("Uploading image...")
        await message.reply_photo(
            "flux_gen.jpg",
            progress=progress,
            progress_args=(ok, time.time(), "Uploading image..."),
        )
        await ok.delete()
        if os.path.exists("flux_gen.jpg"):
            os.remove("flux_gen.jpg")
    except Exception as e:
        await message.edit_text(format_exc(e))


modules_help["fluxai"] = {
    "fluxai [prompt]*": "text to image fluxai",
}
