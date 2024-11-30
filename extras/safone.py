#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import requests
import aiofiles
import base64

from pyrogram import Client, enums, filters
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import MediaCaptionTooLong, MessageTooLong

from utils.misc import prefix, modules_help
from utils.scripts import format_exc

url = "https://api.safone.co"

headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "DNT": "1",
    "Referer": "https://api.safone.dev/docs",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept": "application/json",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}

async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"code": code}) as resp:
            image_data = await resp.read()

    carbon_image = Image.open(BytesIO(image_data))

    enhancer = ImageEnhance.Brightness(carbon_image)
    bright_image = enhancer.enhance(1.0)

    output_image = BytesIO()
    bright_image.save(output_image, format="PNG", quality=95)
    output_image.name = "carbon.png"

    return output_image

async def telegraph(title, user_name, content):
    formatted_content = "<br>".join(content.split("\n"))
    formatted_content = "<p>" + formatted_content + "</p>"

    data = {"title": title, "content": formatted_content, "author_name": user_name}

    response = requests.post(
        url=f"{url}/telegraph/text", headers=headers, json=data, timeout=5
    )

    result = response.json()

    return result["url"]


async def voice_characters():
    response = requests.get(url=f"{url}/speech/characters", headers=headers, timeout=5)

    result = response.json()

    return ", ".join(result["characters"])


async def make_rayso(code: str, title: str, theme: str):
    data = {
        "code": code,
        "title": title,
        "theme": theme,
        "padding": 64,
        "language": "auto",
        "darkMode": False,
    }
    response = requests.post(f"{url}/rayso", data=data, headers=headers)
    if response.status_code != 200:
        return None
    result = response.json()
    try:
        if result["error"] is not None:
            return None
    except KeyError:
        pass
    image_data = result["image"]
    file_name = "rayso.png"
    with open(file_name, "wb") as f:
        f.write(base64.b64decode(image_data))
    return file_name


@Client.on_message(filters.command("asq", prefix) & filters.me)
async def asq(_, message: Message):
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text("Query not provided!")
        return
    await message.edit_text("Processing...")
    response = requests.get(url=f"{url}/asq?query={query}", headers=headers, timeout=5)
    if response.status_code != 200:
        await message.edit_text("Something went wrong!")
        return

    result = response.json()

    ans = result["answer"]
    await message.edit_text(
        f"Q. {query}\n A. {ans}", parse_mode=enums.ParseMode.MARKDOWN
    )


@Client.on_message(filters.command("sgemini", prefix) & filters.me)
async def sgemini(_, message: Message):
    if len(message.command) > 1:
        prompt = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text("prompt not provided!")
        return
    await message.edit_text("Processing...")
    response = requests.get(url=f"{url}/bard?query={prompt}", headers=headers)
    if response.status_code != 200:
        await message.edit_text("Something went wrong!")
        return

    result = response.json()

    ans = result["message"]
    await message.edit_text(
        f"Prompt: {prompt}\n Ans: {ans}", parse_mode=enums.ParseMode.MARKDOWN
    )


@Client.on_message(filters.command("app", prefix) & filters.me)
async def app(client: Client, message: Message):
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
            url=f"{url}/apps?query={query}&limit=1", headers=headers, timeout=5
        )
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()

        try:
            coverImage_url = result["results"][0]["icon"]
            coverImage = requests.get(url=coverImage_url).content
            async with aiofiles.open("coverImage.jpg", mode="wb") as f:
                await f.write(coverImage)

        except Exception:
            coverImage = None

        description = result["results"][0]["description"]
        developer = result["results"][0]["developer"]
        IsFree = result["results"][0]["free"]
        genre = result["results"][0]["genre"]
        package_name = result["results"][0]["id"]
        title = result["results"][0]["title"]
        price = result["results"][0]["price"]
        link = result["results"][0]["link"]
        rating = result["results"][0]["rating"]

        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"<b>Title:</b> <code>{title}</code>\n<b>Rating:</b> <code>{rating}</code>\n<b>IsFree:</b> <code>{IsFree}</code>\n<b>Price:</b> <code>{price}</code>\n<b>Package Name:</b> <code>{package_name}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Developer:</b> <code>{developer}\n<b>Description:</b> {description}\n<b>Link:</b> {link}",
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
                    caption=f"<b>Title:</b> <code>{title}</code>\n<b>Rating:</b> <code>{rating}</code>\n<b>IsFree:</b> <code>{IsFree}</code>\n<b>Price:</b> <code>{price}</code>\n<b>Package Name:</b> <code>{package_name}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Developer:</b> <code>{developer}\n<b>Description:</b> {description}\n<b>Link:</b> {link}",
                )
            ],
        )
    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists("coverImage.jpg"):
            os.remove("coverImage.jpg")


@Client.on_message(filters.command("tsearch", prefix) & filters.me)
async def tsearch(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        limit = 10
        await message.edit_text("Processing...")
        if len(message.command) > 1:
            query = message.text.split(maxsplit=1)[1]
        else:
            message.edit_text(
                "What should i search? You didn't provided me with any value to search"
            )

        response = requests.get(
            url=f"{url}/torrent?query={query}&limit={limit}", headers=headers
        )
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()

        coverImage_url = result["results"][0]["thumbnail"]
        description = result["results"][0]["description"]
        genre = result["results"][0]["genre"]
        category = result["results"][0]["category"]
        title = result["results"][0]["name"]
        link = result["results"][0]["magnetLink"]
        link_result = await telegraph(
            title=title, user_name=message.from_user.first_name, content=link
        )
        language = result["results"][0]["language"]
        size = result["results"][0]["size"]

        results = []

        for i in range(min(limit, len(result["results"]))):
            descriptions = result["results"][i]["description"]
            genres = result["results"][i]["genre"]
            categorys = result["results"][i]["category"]
            titles = result["results"][i]["name"]
            links = result["results"][i]["magnetLink"]
            languages = result["results"][i]["language"]
            sizes = result["results"][i]["size"]

            r = f"<b>Title:</b> <code>{titles}</code>\n<b>Category:</b> <code>{categorys}</code>\n<b>Language:</b> <code>{languages}</code>\n<b>Size:</b> <code>{sizes}</code>\n<b>Genres:</b> <code>{genres}</code>\n<b>Description:</b> {descriptions}\n<b>Magnet Link:</b> <code>{links}</code><br>"
            results.append(r)

        all_results_content = "<br>".join(results)

        link_results = await telegraph(
            title="Search Results",
            user_name=message.from_user.first_name,
            content=all_results_content,
        )

        if coverImage_url is not None:
            coverImage = requests.get(url=coverImage_url).content
            async with aiofiles.open("coverImage.jpg", mode="wb") as f:
                await f.write(coverImage)

            await message.delete()
            await client.send_media_group(
                chat_id,
                [
                    InputMediaPhoto(
                        "coverImage.jpg",
                        caption=f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>\n<b>More Results:</b> <a href='{link_results}'>Click Here</a>",
                    )
                ],
            )
        else:
            await message.edit_text(
                f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>\n<b>More Results:</b> <a href='{link_results}'>Click Here</a>",
                disable_web_page_preview=True,
            )

    except MediaCaptionTooLong:
        description = description[:850]
        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto(
                    "coverImage.jpg",
                    caption=f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>",
                )
            ],
        )

    except MessageTooLong:
        description = description[:150]
        await message.edit_text(
            f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>",
            disable_web_page_preview=True,
        )

    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists("coverImage.jpg"):
            os.remove("coverImage.jpg")


@Client.on_message(filters.command("tts", prefix) & filters.me)
async def tts(client: Client, message: Message):
    characters = await voice_characters()
    await message.edit_text("<code>Please Wait...</code>")
    try:
        if len(message.command) > 2:
            character, prompt = message.text.split(maxsplit=2)[1:]
            if character not in characters:
                await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>"
                )
                return

        elif message.reply_to_message and len(message.command) > 1:
            character = message.text.split(maxsplit=1)[1]
            if character in characters:
                prompt = message.reply_to_message.text
            else:
                await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>"
                )
                return

        else:
            await message.edit_text(
                f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>"
            )
            return

        data = {"text": prompt, "character": character}
        response = requests.post(url=f"{url}/speech", headers=headers, json=data)
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()
        audio_data = result["audio"]
        audio_data = base64.b64decode(audio_data)
        async with aiofiles.open(f"{prompt}.mp3", mode="wb") as f:
            await f.write(audio_data)

        await message.delete()
        await client.send_audio(
            chat_id=message.chat.id,
            audio=f"{prompt}.mp3",
            caption=f"<b>Characters:</b> <code>{character}</code>\n<b>Prompt:</b> <code>{prompt}</code>",
        )
        if os.path.exists(f"{prompt}.mp3"):
            os.remove(f"{prompt}.mp3")

    except KeyError:
        try:
            error = result["error"]
            await message.edit_text(error)
        except KeyError:
            await message.edit_text(
                f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>"
            )
    except Exception as e:
        await message.edit_text(format_exc(e))


@Client.on_message(
    filters.command(["carbonnowsh", "carboon", "carbon", "cboon"], prefix) & filters.me
)
async def carbon(client: Client, message: Message):
    if message.reply_to_message:
        text = message.reply_to_message.text
        message_id = message.reply_to_message.id
    elif len(message.command) > 1:
        message_id = None
        text = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text("Query not provided!")
        return
    await message.edit_text("Processing...")

    image_file = await make_carbon(text)

    await message.delete()
    try:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=image_file,
            caption=f"<b>Text:</b> <code>{text}</code>",
            reply_to_message_id=message_id,
        )
    except MediaCaptionTooLong:
        cap = text[:850]
        await client.send_photo(
            chat_id=message.chat.id,
            photo=image_file,
            caption=f"<b>Text:</b> <code>{cap}</code>",
            reply_to_message_id=message_id,
        )
    except Exception as e:
        await message.edit_text(format_exc(e))
    if os.path.exists("carbon.png"):
        os.remove("carbon.png")


@Client.on_message(filters.command("ccgen", prefix) & filters.me)
async def ccgen(_, message: Message):
    if len(message.command) > 1:
        bins = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text("Code not provided!")
        return
    await message.edit_text("Processing...")
    response = requests.get(url=f"{url}/ccgen?bins={bins}", headers=headers)
    if response.status_code != 200:
        await message.edit_text("Something went wrong")
        return

    result = response.json()

    cards = result["results"][0]["cards"]
    cards_str = "\n".join([f'"{card}"' for card in cards])
    bins = result["results"][0]["bin"]
    await message.edit_text(
        f"Bins: <code>{bins}</code>\nTotal: <code>{len(cards)}</code>\nCards: \n<code>{cards_str}</code>"
    )


@Client.on_message(filters.command("rayso", prefix) & filters.me)
async def rayso(client: Client, message: Message):
    title = "Untitled"
    themes = [
        "vercel",
        "supabase",
        "tailwind",
        "clerk",
        "mintlify",
        "prisma",
        "bitmap",
        "noir",
        "ice",
        "sand",
        "forest",
        "mono",
        "breeze",
        "candy",
        "crimson",
        "falcon",
        "meadow",
        "midnight",
        "raindrop",
        "sunset",
    ]
    if message.reply_to_message:
        text = message.reply_to_message.text
        message_id = message.reply_to_message.id
        if 2 <= len(message.command) <= 3:
            title = message.text.split(maxsplit=2)[1]
            theme = message.text.split(maxsplit=2)[2].lower()
            if theme not in themes:
                theme = "breeze"
    elif len(message.command) > 1:
        message_id = message.id
        title = message.text.split(maxsplit=3)[1]
        theme = message.text.split(maxsplit=3)[2]
        if theme not in themes:
            theme = "breeze"
        text = message.text.split(maxsplit=3)[3]
    else:
        await message.edit_text("Query not provided!")
        return
    await message.edit_text("Processing...")

    image_file = await make_rayso(text, title, theme)

    if image_file is None:
        await message.edit_text("Something went wrong")
        return
    try:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=image_file,
            caption=f"<b>Text:</b> <code>{text}</code>",
            reply_to_message_id=message_id,
        )
        await message.delete()
    except MediaCaptionTooLong:
        cap = text[:850]
        await client.send_photo(
            chat_id=message.chat.id,
            photo=image_file,
            caption=f"<b>Text:</b> <code>{cap}</code>",
            reply_to_message_id=message_id,
        )
        await message.delete()
    except Exception as e:
        await message.edit_text(format_exc(e))
    if os.path.exists(image_file):
        os.remove(image_file)


modules_help["safone"] = {
    "asq [query]*": "Asq",
    "app [query]*": "Search for an app on Play Store",
    "tsearch [query]*": "Search Torrent",
    "tts [character]* [text/reply to text]*": "Convert Text to Speech",
    "sgemini [prompt]*": "Gemini Model through safone api",
    "carbon [code/file/reply]": "Create beautiful image with your code",
    "ccgen [bins]*": "Generate credit cards",
    "rayso [title]* [theme]* [text/reply to text]*": "Create beautiful image with your text",
}
