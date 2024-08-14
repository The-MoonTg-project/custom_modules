import os
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix


def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Pyrogram command handler for the job commandx
@Client.on_message(filters.command("injob", prefix) & filters.me)
async def gov_job(client: Client, message: Message):
    await message.edit_text("Fetching job information...")

    try:
        html_data = fetch_data("https://www.sarkariresult.com/latestjob.php")
    except requests.exceptions.HTTPError:
        return await message.edit_text("API URL refused connection")
    soup = BeautifulSoup(html_data, "html.parser")

    job_info = ""
    for div in soup.find_all("div", id="post"):
        job_info += div.get_text()

    with open("jobs.txt", "w") as job_file:
        job_file.write("Information for Jobs Gathered Successfully\n\n" + job_info)

    await client.send_document(
        chat_id=message.chat.id,
        document="jobs.txt",
        caption="Job information fetched successfully",
    )
    os.remove("jobs.txt")


modules_help["injob"] = {"injob": "Get government job information for IN"}
