import requests
from bs4 import BeautifulSoup

import random
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.scripts import get_text, format_exc
from utils.misc import prefix, modules_help


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
            await message.edit_text(f"Error: {error_message}")
        else:
            if len(news_data) > 0:
                news_item = random.choice(news_data)

                title = news_item["title"]
                excerpt = news_item["excerpt"]
                source = news_item["source"]
                relative_time = news_item["relative_time"]
                news_url = news_item["url"]

                message_text = f"𝗧𝗜𝗧𝗟𝗘: {title}\n𝗦𝗢𝗨𝗥𝗖𝗘: {source}\n𝗧𝗜𝗠𝗘: {relative_time}\n𝗘𝗫𝗖𝗘𝗥𝗣𝗧: {excerpt}\n𝗨𝗥𝗟: {news_url}"
                await message.edit_text(message_text)
            else:
                await message.edit_text("No news found.")

    except Exception as e:  # Replace with specific exception type if possible
        return await message.edit_text(format_exc(e))
    

@Client.on_message(filters.command("nasa", prefix) & filters.me)
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
        return await message.edit_text(format_exc(e))


@Client.on_message(filters.command("hastag", prefix) & filters.me)
async def hastag(bot: Client, message: Message):
    global content
    url = "https://all-hashtag.com/library/contents/ajax_generator.php"
    try:
        text = message.text.split(' ',1)[1]
        data = dict(keyword=text, filter="top")

        res = requests.post(url, data).text

        content = BSP(res, 'html.parser').find("div", {"class":"copy-hashtags"}).string
    except IndexError:
        return await message.edit_text("✦ Example ➠ /hastag python")
        
    
    await message.edit_text(f"✦ ʜᴇʀᴇ ɪs ʏᴏᴜʀ  ʜᴀsᴛᴀɢ ➠\n\n<pre>{content}</pre>", quote=True)


@Client.on_message(filters.command("coub", prefix) & filters.me)
async def coub(c: Client, m: Message):
    if len(m.command) == 1:
        await m.edit_text((" /coub search query — Sends a random Coub (short video) from search results."))
        return

    text = m.text.split(maxsplit=1)[1]
    r = await http.get("https://coub.com/api/v2/search/coubs", params={"q": text})
    rjson = r.json()
    try:
        content = random.choice(rjson["coubs"])
        links = content["permalink"]
        title = content["title"]
    except IndexError:
        await m.edit_text("nothing found")
    else:
        await m.edit_text(f'<b><a href="https://coub.com/v/{links}">{title}</a></b>')


modules_help["useless"] = {
    "coub": "Gets the short video ."
    + "\n\nUsage: `.coub <keywords>`"
    + "\n\nExample: `.coub technology `",
    "news": "Gets the news of a  catagory."
    + "\n\nUsage: `.news <catagory> `"
    + "\n\nExample: `.news political`",
    "hastag": "genarate  #hastag  ."
    + "\n\nUsage: `.hastag <keywords>`"
    + "\n\nExample: `.hastag technology `",
    "nasa": "Gets the daily  nasa  news ."
    + "\n\nUsage: `.nasa`"
    + "\n\nExample: `.nasa `"
}
