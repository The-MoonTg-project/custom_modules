import os
import requests
import aiofiles

from pyrogram import Client, filters, enums
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import MediaCaptionTooLong

from utils.misc import prefix, modules_help
from utils.scripts import format_exc

url = "https://api.safone.co"

headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "DNT": "1",
    "Referer": "https://api.safone.co/docs",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept": "application/json",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}


@Client.on_message(filters.command("anime_search", prefix) & filters.me)
async def anime_search(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        await message.edit_text("Processing...")
        if len(message.command) > 1:
            query = message.text.split(maxsplit=1)[1]
        else:
            message.edit_text(
                "What should i search? You didn't provided me with any value to search"
            )

        response = requests.get(
            url=f"{url}/anime/search?query={query}", headers=headers, timeout=5
        )
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()

        averageScore = result["averageScore"]
        try:
            coverImage_url = result["imageUrl"]
            coverImage = requests.get(url=coverImage_url).content
            async with aiofiles.open("coverImage.jpg", mode="wb") as f:
                await f.write(coverImage)

        except Exception:
            coverImage = None

        title = result["title"]["english"]
        trailer = result["trailer"]["id"]
        description = result["description"]
        episodes = result["episodes"]
        genres = ", ".join(result["genres"])
        isAdult = result["isAdult"]
        status = result["status"]
        studios = ", ".join(result["studios"])

        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"<b>Title:</b> <code>{title}</code>\n<b>Average Score:</b> <code>{averageScore}</code>\n<b>Status:</b> <code>{status}</code>\n<b>Genres:</b> <code>{genres}</code>\n<b>Episodes:</b> <code>{episodes}</code>\n<b>Is Adult:</b> <code>{isAdult}</code>\n<b>Studios:</b> <code>{studios}</code>\n<b>Description:</b> <code>{description}</code>\n<b>Trailer:</b> <a href='https://youtu.be/{trailer}'>Click Here</a>",
                )
            ],
        )

    except MediaCaptionTooLong:
        description = description[:850]
        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"<b>Title:</b> <code>{title}</code>\n<b>Average Score:</b> <code>{averageScore}</code>\n<b>Status:</b> <code>{status}</code>\n<b>Genres:</b> <code>{genres}</code>\n<b>Episodes:</b> <code>{episodes}</code>\n<b>Is Adult:</b> <code>{isAdult}</code>\n<b>Studios:</b> <code>{studios}</code>\n<b>Description:</b> <code>{description}</code>\n<b>Trailer:</b> <a href='https://youtu.be/{trailer}'>Click Here</a>",
                )
            ],
        )
    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists("coverImage.jpg"):
            os.remove("coverImage.jpg")


@Client.on_message(filters.command("manga_search", prefix) & filters.me)
async def manga_search(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        await message.edit_text("Processing...")
        if len(message.command) > 1:
            query = message.text.split(maxsplit=1)[1]
        else:
            message.edit_text(
                "What should i search? You didn't provided me with any value to search"
            )

        response = requests.get(
            url=f"{url}/anime/manga?query={query}", headers=headers, timeout=5
        )
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()

        averageScore = result["averageScore"]
        try:
            coverImage_url = result["imageUrl"]
            coverImage = requests.get(url=coverImage_url).content
            async with aiofiles.open("coverImage.jpg", mode="wb") as f:
                await f.write(coverImage)

        except Exception:
            coverImage = None

        title = result["title"]["english"]
        trailer = result["trailer"]["id"]
        description = result["description"]
        chapters = result["chapters"]
        genres = ", ".join(result["genres"])
        isAdult = result["isAdult"]
        status = result["status"]
        studios = ", ".join(result["studios"])

        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"<b>Title:</b> <code>{title}</code>\n<b>Average Score:</b> <code>{averageScore}</code>\n<b>Status:</b> <code>{status}</code>\n<b>Genres:</b> <code>{genres}</code>\n<b>Chapters:</b> <code>{chapters}</code>\n<b>Is Adult:</b> <code>{isAdult}</code>\n<b>Studios:</b> <code>{studios}</code>\n<b>Description:</b> <code>{description}</code>\n<b>Trailer:</b> <a href='https://youtu.be/{trailer}'>Click Here</a>",
                )
            ],
        )

    except MediaCaptionTooLong:
        description = description[:850]
        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"<b>Title:</b> <code>{title}</code>\n<b>Average Score:</b> <code>{averageScore}</code>\n<b>Status:</b> <code>{status}</code>\n<b>Genres:</b> <code>{genres}</code>\n<b>Chapters:</b> <code>{chapters}</code>\n<b>Is Adult:</b> <code>{isAdult}</code>\n<b>Studios:</b> <code>{studios}</code>\n<b>Description:</b> <code>{description}</code>\n<b>Trailer:</b> <a href='https://youtu.be/{trailer}'>Click Here</a>",
                )
            ],
        )
    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists("coverImage.jpg"):
            os.remove("coverImage.jpg")


@Client.on_message(filters.command("character", prefix) & filters.me)
async def character(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        await message.edit_text("Processing...")
        if len(message.command) > 1:
            query = message.text.split(maxsplit=1)[1]
        else:
            message.edit_text(
                "What should i search? You didn't provided me with any value to search"
            )

        response = requests.get(
            url=f"{url}/anime/character?query={query}", headers=headers, timeout=5
        )
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()

        try:
            coverImage_url = result["image"]["large"]
            coverImage = requests.get(url=coverImage_url).content
            async with aiofiles.open("coverImage.jpg", mode="wb") as f:
                await f.write(coverImage)

        except Exception:
            coverImage = None

        age = result["age"]
        description = result["description"]
        height = result["height"]
        name = result["name"]["full"]
        native_name = result["name"]["native"]
        read_more = result["siteUrl"]

        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"**Name:** `{name}`\n**Native Name:** `{native_name}`\n**Age:** `{age}`\n**Height:** {height}\n**Description:** `{description}`[read more...]({read_more})",
                    parse_mode=enums.ParseMode.MARKDOWN,
                )
            ],
        )

    except MediaCaptionTooLong:
        description = description[:850]
        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"**Name:** `{name}`\n**Native Name:** `{native_name}`\n**Age:** `{age}`\n**Height:** {height}\n**Description:** `{description}`[read more...]({read_more})",
                    parse_mode=enums.ParseMode.MARKDOWN,
                )
            ],
        )
    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists("coverImage.jpg"):
            os.remove("coverImage.jpg")


modules_help["anilist"] = {
    "anime_search": "Search for anime on Anilist",
    "manga_search": "Search for manga on Anilist",
    "character": "Search for character on Anilist",
}
