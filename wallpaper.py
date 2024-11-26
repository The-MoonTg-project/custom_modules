#wallpaper

from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
from requests import get
from utils.misc import modules_help, prefix


@Client.on_message(filters.command("wallpaper", prefix) & filters.me)
async def WallpapersCom(client, message):
    chat_id = message.chat.id
    try:
        query = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply("Input image name for search 🔍")

    msg = await message.reply("🔍")

    # Fetch wallpapers from the API
    try:
        response = get(f"https://hoshi-api-f62i.onrender.com/api/wallpaper?query={query}")
        response.raise_for_status()  # Raise error for HTTP issues
        images = response.json()
    except Exception as e:
        return await msg.edit(f"Error fetching wallpapers: {e}")

    if not images or "images" not in images:
        return await msg.edit(
            f"**✨ No wallpapers found for query: `{query}`. Try another search ❤️**"
        )

    media_group = []
    count = 0

    # Add wallpapers to the media group
    for url in images["images"][:8]:
        media_group.append(InputMediaPhoto(media=url, has_spoiler=True))
        count += 1

    await msg.edit(f"⚡ Fetched {count} wallpapers...")

    try:
        # Send the media group
        await client.send_media_group(
            chat_id=chat_id,
            media=media_group,
            reply_to_message_id=message.id
        )
        await msg.delete()
    except Exception as e:
        await msg.delete()
        await message.reply(f"Error sending wallpapers: {e}")


modules_help["wallpaper"] = {
    "wallpaper": "search wallpaper",
}
