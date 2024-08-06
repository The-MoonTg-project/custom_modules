from pyrogram import Client, filters, enums
from pyrogram.types import Message, InputMediaPhoto
from io import BytesIO
from PIL import Image
import requests
import asyncio
from utils.misc import modules_help, prefix

API_URL = "https://bk9.fun/search/unsplash?q="


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
            image_bytes.seek(0)  # Reset pointer if not resized
            return image_bytes
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_bytes


async def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img_bytes = BytesIO(response.content)
            resized_img_bytes = resize_image(img_bytes)
            return resized_img_bytes
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None


@Client.on_message(filters.command(["unsplash2", "usp2"], prefix) & filters.me)
async def imgsearch(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit(
            "Usage: `img [number] <query>`", parse_mode=enums.ParseMode.MARKDOWN
        )
        return

    num_pics = int(message.command[1]) if message.command[1].isdigit() else 10
    query = " ".join(message.command[2:])

    # Update status
    status_message = await message.edit(
        "Searching for images...", parse_mode=enums.ParseMode.MARKDOWN
    )

    url = f"{API_URL}{query}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("status"):
            urls = data.get("BK9", [])[:num_pics]
            images = [download_image(img_url) for img_url in urls]

            # Download images
            downloaded_images = await asyncio.gather(*images)

            media = [
                InputMediaPhoto(media=img_bytes)
                for img_bytes in downloaded_images
                if img_bytes
            ]

            if media:
                await status_message.edit(
                    "Uploading pictures...", parse_mode=enums.ParseMode.MARKDOWN
                )
                while media:
                    batch = media[:10]
                    media = media[10:]
                    await message.reply_media_group(batch)
                await status_message.delete()  # Delete status message after uploading
            else:
                await status_message.edit(
                    "No valid images found.", parse_mode=enums.ParseMode.MARKDOWN
                )
        else:
            await status_message.edit(
                "No images found for the given query.",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
    else:
        await status_message.edit(
            "An error occurred, please try again later.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )


modules_help["unsplash2"] = {
    "unsplash2 [number]* [query]": "Get HD images. Default number of images is 10",
    "usp2 [number]* [query]": "Get HD images. Default number of images is 10",
}
