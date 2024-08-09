from utils.misc import prefix, modules_help
from pyrogram.errors import RPCError
import requests
from bs4 import BeautifulSoup

import random
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

NEWS_URL = "https://sugoi-api.vercel.app/news?keyword={}"


@app.on_message(filters.command("news"))
async def enews(_, message):
    keyword = (
        message.text.split(" ", 1)[1].strip() if len(message.text.split()) > 1 else ""
    )
    url = NEWS_URL.format(keyword)

    try:
        response = await state.get(url)  # Assuming state is an asynchronous function
        news_data = response.json()

        if "error" in news_data:
            error_message = news_data["error"]
            await message.reply_text(f"Error: {error_message}")
        else:
            if len(news_data) > 0:
                news_item = random.choice(news_data)

                title = news_item["title"]
                excerpt = news_item["excerpt"]
                source = news_item["source"]
                relative_time = news_item["relative_time"]
                news_url = news_item["url"]

                message_text = f"𝗧𝗜𝗧𝗟𝗘: {title}\n𝗦𝗢𝗨𝗥𝗖𝗘: {source}\n𝗧𝗜𝗠𝗘: {relative_time}\n𝗘𝗫𝗖𝗘𝗥𝗣𝗧: {excerpt}\n𝗨𝗥𝗟: {news_url}"
                await message.reply_text(message_text)
            else:
                await message.reply_text("No news found.")

    except Exception as e:  # Replace with specific exception type if possible
        await message.reply_text(f"Error: {str(e)}")


modules_help["news"] = {
    "specs": "Gets the news of a  catagory."
    + "\n\nUsage: `.news <catagory> `"
    + "\n\nExample: `.news political`"
}


from pyrogram import Client
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Chat, Message, User


def get_text(message: Message) -> [None, str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@Client.on_message(filters.command("cedit"))
async def loltime(client, message):
    lol = await message.reply("Processing please wait")
    cap = get_text(message)
    if not message.reply_to_message:
        await lol.edit("reply to any message to edit caption")
    reply = message.reply_to_message
    try:
        await reply.copy(message.chat.id, caption=cap)
        await lol.delete()
    except RPCError as i:
        await lol.edit(i)
        return
      
modules_help["cedit"] = {
    "specs": "Gets edit caption."
    + "\n\nUsage: `.cedit <reply caption> `"
    + "\n\nExample: `.cedit reply caption`"
}





async def eod(message, error):
    await message.reply_text(f"An error occurred: {error}")
    



@Client.on_message(filters.command("nasa"))
async def aposj(client, message):
    link = "https://apod.nasa.gov/apod/"
    C = requests.get(link).content
    m = BeautifulSoup(C, "html.parser", from_encoding="utf-8")
    try:
        try:
            img = m.find_all("img")[0]["src"]
            img = link + img
        except IndexError:
            img = None
        expla = m.find_all("p")[2].text.replace("\n", " ")
        expla = expla.split("     ")[0]
        if len(expla) > 3000:
            expla = expla[:3000] + "..."
        expla = "" + expla + ""
        await client.send_photo(message.chat.id, photo=img, caption=expla)
        if message.outgoing:
            await message.delete()
    except Exception as e:
        return await eod(message, str(e))


modules_help["nasa"] = {
    "specs": "Gets the daily  nasa  news ."
    + "\n\nUsage: `.nasa`"
    + "\n\nExample: `.nasa `"
}
