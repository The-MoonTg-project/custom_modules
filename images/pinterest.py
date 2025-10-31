from pyrogram import Client, filters, enums
from pyrogram.types import Message, InputMediaPhoto
from io import BytesIO
from PIL import Image
import aiohttp, asyncio
from utils.misc import modules_help, prefix

SEARCH_API = "https://api.nekolabs.web.id/discovery/pinterest/search?q="
DOWNLOAD_API = "https://delirius-apiofc.vercel.app/download/pinterestdl?url="

def resize_image(image_bytes):
    try:
        with Image.open(image_bytes) as img:
            max_size = (1280, 1280)
            if img.size > max_size:
                img.thumbnail(max_size)
                output = BytesIO()
                img.save(output, format="JPEG")
                output.seek(0)
                return output
            image_bytes.seek(0)
            return image_bytes
    except Exception:
        return image_bytes

async def download_image(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    img_bytes = BytesIO(await resp.read())
                    return resize_image(img_bytes)
    except:
        return None

async def download_video(url, path="pinterest.mp4"):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(path, "wb") as f:
                        f.write(await resp.read())
                    return path
    except:
        return None

@Client.on_message(filters.command("pinterest", prefix) & filters.me)
async def pinterest_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit(
            "Usage:\n"
            "`pinterest <number> <query>`\n"
            "or\n"
            "`pinterest <Pinterest link>`",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return

    query = " ".join(message.command[1:])
    if "pinterest.com" in query or "pin.it" in query:
        await message.edit("Downloading Pinterest media...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{DOWNLOAD_API}{query}") as resp:
                if resp.status != 200:
                    await message.edit("Failed to fetch Pinterest media.")
                    return
                data = await resp.json()

        if not data.get("status") or "data" not in data:
            await message.edit("Invalid Pinterest link or download unavailable.")
            return

        media_data = data["data"]["download"]
        title = data["data"].get("title", "Pinterest Media")

        if media_data["type"] == "video":
            path = await download_video(media_data["url"])
            if path:
                await message.delete()
                await message.reply_video(path, caption=title)
            else:
                await message.edit("Failed to download video.")
        else:
            image_bytes = await download_image(media_data["url"])
            if image_bytes:
                await message.delete()
                await message.reply_photo(image_bytes, caption=title)
            else:
                await message.edit("Failed to download image.")
        return

    if message.command[1].isdigit():
        if len(message.command) < 3:
            await message.edit(
                "Usage:\n"
                "`pinterest <number> <query>`\n"
                "or\n"
                "`pinterest <Pinterest link>`",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        num_pics = max(1, min(30, int(message.command[1])))
        query = " ".join(message.command[2:])
    else:
        num_pics = 10
        query = " ".join(message.command[1:])

    status = await message.edit("Searching Pinterest...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SEARCH_API}{query}") as resp:
            if resp.status != 200:
                await status.edit("API request failed.")
                return
            data = await resp.json()

    if not data.get("success") or not data.get("result"):
        await status.edit("No results found.")
        return

    results = data["result"][:num_pics]
    urls = [r["imageUrl"] for r in results if "imageUrl" in r]
    if not urls:
        await status.edit("No valid images found.")
        return

    semaphore = asyncio.Semaphore(5)
    async def safe_download(u):
        async with semaphore:
            return await download_image(u)

    downloaded = await asyncio.gather(*[safe_download(u) for u in urls])
    media = [InputMediaPhoto(media=i) for i in downloaded if i]

    if not media:
        await status.edit("Failed to download images.")
        return

    await status.edit("Uploading images...")
    for i in range(0, len(media), 10):
        batch = media[i:i + 10]
        try:
            await message.reply_media_group(batch)
            await asyncio.sleep(1)
        except:
            continue
    await status.delete()

modules_help["pinterest"] = {
    "pinterest <number> <query>": "Search Pinterest and get images.",
    "pinterest <link>": "Download media directly from a Pinterest link.",
}
