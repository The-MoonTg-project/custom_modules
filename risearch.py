from utils.misc import modules_help, prefix
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from modules.url import generate_screenshot
import os

# API endpoints for reverse image search engines
SEARCH_ENGINES = {
    "lens": "https://lens.google.com/uploadbyurl?url={image}",
    "reverse": "https://www.google.com/searchbyimage?sbisrc=4chanx&image_url={image}&safe=off",
    "tineye": "https://www.tineye.com/search?url={image}",
    "bing": "https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIVSP&sbisrc=UrlPaste&q=imgurl:{image}",
    "yandex": "https://yandex.com/images/search?source=collections&&url={image}&rpt=imageview",
    "saucenao": "https://saucenao.com/search.php?db=999&url={image}",
}


@Client.on_message(filters.command("risearch", prefix) & filters.reply)
async def reverse_image_search(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text(
            f"Please reply to an image with <code>{prefix}risearch [engine]</code> or <code>{prefix}risearch</code>."
        )
        return

    command_parts = message.text.split(maxsplit=1)
    engines_to_use = (
        [command_parts[1].strip().lower()]
        if len(command_parts) > 1 and command_parts[1].strip()
        else list(SEARCH_ENGINES.keys())
    )

    invalid_engines = [
        engine for engine in engines_to_use if engine not in SEARCH_ENGINES
    ]
    if invalid_engines:
        await message.reply_text(
            f"Invalid engine(s): {', '.join(invalid_engines)}. Available: {', '.join(SEARCH_ENGINES.keys())}"
        )
        return

    processing_message = await message.edit_text("Processing the image...")

    try:
        # Download and upload the image
        photo_path = await message.reply_to_message.download()
        img_url = upload_image(photo_path)
        print(img_url)
        if not img_url:
            await processing_message.edit("Error: Could not upload the image.")
            return

        # Perform searches for the selected engines
        for engine in engines_to_use:
            search_url = SEARCH_ENGINES[engine].format(image=img_url)
            await send_screenshot(client, message, search_url, engine)
    except Exception as e:
        await processing_message.edit(f"An error occurred: {e}")
    finally:
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)


def upload_image(photo_path):
    """Uploads an image to tmpfiles.org and returns the direct download URL."""
    try:
        with open(photo_path, "rb") as image_file:
            response = requests.post(
                "https://tmpfiles.org/api/v1/upload", files={"file": image_file}
            )
        if response.status_code == 200:
            data = response.json()
            url = data["data"]["url"]
            pic_url = url.split("/")[-2] + "/" + url.split("/")[-1]
            direct_download_url = url.replace(f"/{pic_url}", f"/dl/{pic_url}")
            print(direct_download_url)
            return direct_download_url
        else:
            return None
    except Exception:
        return None


async def send_screenshot(client, message, url, engine_name):
    """Takes a screenshot of the URL and sends it to the chat."""
    screenshot_data = generate_screenshot(url)
    if screenshot_data:
        await client.send_photo(
            message.chat.id,
            screenshot_data,
            caption=f"<b>{engine_name.capitalize()} Result</b>\nURL: <code>{url}</code>",
            reply_to_message_id=message.id,
        )
    else:
        await message.reply(
            f"Failed to take screenshot for {engine_name.capitalize()}."
        )


# Add module details to help
modules_help["risearch"] = {
    "risearch": f"Reply to a photo with `{prefix}risearch [engine]` (e.g., `{prefix}risearch lens`, `{prefix}risearch bing`) "
    f"\nor use `{prefix}risearch` to analyze the image with all engines.",
}
