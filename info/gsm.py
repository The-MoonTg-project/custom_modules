from pyrogram import Client, filters

import requests

from utils.misc import prefix, modules_help


def fetch_gsm_data(query):
    url = "https://www.samirxpikachu.run.place/phonelink"
    querystring = {"search": query}
    response = requests.get(url, params=querystring)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@Client.on_message(filters.command("gsm", prefix) & filters.me)
async def gsmsearch(client, message):
    if len(message.text.split()) < 2:
        await message.edit_text("Please provide a search query.")
        return

    await message.edit_text("Searching...")
    query = message.text.split(None, 1)[1]  # Extract the query from the command
    results = fetch_gsm_data(query)

    if results:
        for item in results:
            title = item.get("title", "No title")
            thumb = item.get("thumb", "")
            link = item.get("link", "")

            await message.reply_photo(
                photo=thumb, caption=f"<a href='{link}'>{title}</a>"
            )
    else:
        await message.edit_text("No results found.")


modules_help["gsm"] = {"gsm [query]": "Search for GSM information using a query."}
