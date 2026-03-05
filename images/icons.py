import os

import aiohttp
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message

from utils import modules_help, prefix


@Client.on_message(filters.command("icons", prefix) & filters.me)
async def icons(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text(
            f"<b>Usage: </b><code>{prefix}icons [query]</code>"
        )
    query = message.text.split(maxsplit=1)[1]
    await message.edit_text("<code>Searching for icons...</code>")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    urls = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"https://www.flaticon.com/search?type=icon&word={query}&license=selection&order_by=4",
                headers=headers,
            ) as resp:
                html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            icons_list = soup.find_all("img", class_="lzy")

            for icon in icons_list[:10]:
                src = icon.get("data-src") or icon.get("src")
                if src:
                    urls.append(src)
        except Exception:
            pass

        if not urls:
            try:
                async with session.get(
                    f"https://www.freepik.com/search?format=search&query={query}&type=icon",
                    headers=headers,
                ) as resp:
                    html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                icons_list = soup.find_all("img")
                for icon in icons_list[:10]:
                    src = icon.get("src")
                    if src and "icon" in src.lower():
                        urls.append(src)
            except Exception:
                pass

        if not urls:
            await message.edit_text("No icons found.")
            return

        result = []
        for icon_url in urls:
            try:
                async with session.get(icon_url) as resp:
                    if resp.status == 200:
                        img_data = await resp.read()
                        fname = f"icon_{urls.index(icon_url)}.png"
                        with open(fname, "wb") as f:
                            f.write(img_data)
                        result.append(fname)
            except Exception:
                continue

    if not result:
        await message.edit_text("No icons found.")
        return

    media = []
    for i, img in enumerate(result):
        media.append(
            InputMediaPhoto(
                img,
                caption=f"<b>{query} icons</b> ({i + 1}/{len(result)})"
                if i == 0
                else "",
            )
        )

    try:
        await client.send_media_group(message.chat.id, media)
    except Exception as e:
        await message.edit_text(f"Error: {e}")
    finally:
        for img in result:
            if os.path.exists(img):
                os.remove(img)
    await message.delete()


modules_help["icons"] = {
    "icons [query]*": "Search for icons on Flaticon and Freepik",
}
