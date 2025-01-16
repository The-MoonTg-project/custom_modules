from pyrogram import Client, filters, enums
import requests
import asyncio
from pyrogram.types import Message
from utils.misc import modules_help, prefix




APTOIDE_API_URL = "https://ws75.aptoide.com/api/7/listSearchApps"

# Function to fetch APK details from Aptoide
def fetch_apk_details(query):
    params = {"query": query}
    response = requests.get(APTOIDE_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "datalist" in data and "list" in data["datalist"]:
            return data["datalist"]["list"]
        else:
            return []
    else:
        return []

@Client.on_message(filters.command("aptoide", prefix) & filters.me)
async def aptoide(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: {prefix}aptoide <app_name>")
        return

    query = " ".join(message.command[1:])
    results = fetch_apk_details(query)  # Define this function to fetch APK details

    if not results:
        await message.edit_text("❌ No results found for your query.")
        return

    # Limit results to 5
    results = results[:5]

    for app in results:
        name = app.get("name", "N/A")
        package = app.get("package", "N/A")
        uname = app.get("uname", "N/A")
        size = app.get("size", 0)
        icon = app.get("icon", "")
        graphic = app.get("graphic", "")
        added = app.get("added", "N/A")
        modified = app.get("modified", "N/A")
        updated = app.get("updated", "N/A")
        uptype = app.get("uptype", "N/A")
        developer = app.get("developer", {}).get("name", "N/A")

        file_info = app.get("file", {})
        vername = file_info.get("vername", "N/A")
        vercode = file_info.get("vercode", "N/A")
        md5sum = file_info.get("md5sum", "N/A")
        filesize = file_info.get("filesize", 0)
        path = file_info.get("path", "N/A")
        path_alt = file_info.get("path_alt", "N/A")
        malware_rank = file_info.get("malware", {}).get("rank", "Unknown")

        response_text = (
            f"📱 **App Name:** {name}\n"
            f"📦 **Package Name:** {package}\n"
            f"🔑 **Unique Name:** {uname}\n"
            f"📏 **Size:** {size / (1024 * 1024):.2f} MB\n"
            f"🗓️ **Added On:** {added}\n"
            f"🛠️ **Last Modified:** {modified}\n"
            f"🔄 **Last Updated:** {updated}\n"
            f"📤 **Upload Type:** {uptype}\n"
            f"👨‍💻 **Developer:** {developer}\n\n"
            f"📂 **File Details:**\n"
            f"🆕 **Version Name:** {vername}\n"
            f"🔢 **Version Code:** {vercode}\n"
            f"🔒 **MD5 Checksum:** {md5sum}\n"
            f"📂 **File Size:** {filesize / (1024 * 1024):.2f} MB\n"
            f"📥 **Download Link:** [Primary]({path}) | [Alternate]({path_alt})\n"
            f"✅ **Malware Rank:** {malware_rank}\n\n"
            f"🖼️ **Icon:** [Link]({icon})\n"
            f"🎨 **Graphic:** [Link]({graphic})"
        )

        await message.edit_text(response_text, disable_web_page_preview=True)


modules_help["ipinfo"] = {"aptoide [apk name]*": "apk search"}
