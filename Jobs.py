import html
import json
import os
import re
from pyrogram import Client, filters
import aiohttp
import httpx
from bs4 import BeautifulSoup
from utils.misc import modules_help, prefix


def getdata(url):
        r = requests.get(url)
        return r.text






@Client.on_message(filters.command("job"))
async def govjob(client: Client, message: Message):
    await message.reply_text("Trying To Fetch Jobs...")
    res = ""
    htmldata = getdata("https://www.sarkariresult.com/latestjob.php")

    soup = BeautifulSoup(htmldata, "html.parser")

    for li in soup.find_all("div", id="post"):
        res += li.get_text()

    lmao = "Information for Jobs Gathered Successfully\n\n" + str(res)

    with open("jobs.txt", "w") as job:
        job.write(lmao)
    await client.send_document(
        chat_id=message.chat.id,
        document="jobs.txt",
        caption="Information for Jobs Gathered Successfully",
        
    )

modules_help["job"] = {
    "job"
}
