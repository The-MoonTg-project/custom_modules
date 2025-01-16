import os
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

from utils.scripts import  import_library


google_play_scraper = import_library("google_play_scraper")

from google_play_scraper import app, search


@Client.on_message(filters.command("gapp", prefix) & filters.me)
async def app_details(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Please provide the app package name. 📝\nUsage: {prefix}gapp [package name]")
        return

    package_name = message.command[1]
    await message.edit_text(f"Fetching details for: **{package_name}** 🔍")

    try:
        details = app(package_name, lang="en", country="in")
        
        # Create response text with emojis
        response_text = f"**{details['title']}** 📱\n"
        response_text += f"**Developer:** {details['developer']} 👨‍💻\n"
        response_text += f"**Developer Address:** {details.get('developerAddress', 'N/A')} 🏠\n"
        response_text += f"**Rating:** {details['score']} ⭐ ({details['ratings']} ratings, {details['reviews']} reviews) 💬\n"
        response_text += f"**Installs:** {details['installs']} 📦\n"
        response_text += f"**Genre:** {details['genre']} 🎮 ({details.get('genreId', 'N/A')})\n"
        response_text += f"**App ID:** {details.get('appId', 'N/A')} 🆔\n"
        response_text += f"**Content Rating:** {details.get('contentRating', 'N/A')} 🏷️\n"  # Added contentRating
        response_text += f"**Content Rating Description:** {details.get('contentRatingDescription', 'N/A')} 📜\n"  # Added contentRatingDescription
        response_text += f"**Ad Supported:** {'Yes' if details.get('adSupported', False) else 'No'} 🎬\n"  # Added adSupported
        response_text += f"**Contains Ads:** {'Yes' if details.get('containsAds', False) else 'No'} 📺\n"  # Added containsAds
        response_text += f"**Released:** {details.get('released', 'N/A')} 🗓️\n"  # Added released date
        response_text += f"**Updated:** {details.get('updated', 'N/A')} ⏰\n"  # Added updated timestamp
        response_text += f"**Version:** {details.get('version', 'N/A')} 🔢\n"  # Added version

        response_text += "**Categories:** 📂\n"
        for category in details.get("categories", []):
            response_text += f"  - {category['name']} ({category.get('id', 'N/A')}) 🏷️\n"
        response_text += f"**Offers IAP:** {'Yes' if details['offersIAP'] else 'No'} 💸\n"
        response_text += f"**IAP Range:** {details.get('inAppProductPrice', 'N/A')} 💰\n"
        response_text += f"[Developer Website]({details.get('developerWebsite', 'N/A')}) 🌐 | "
        response_text += f"[Privacy Policy]({details.get('privacyPolicy', 'N/A')}) 🔒\n"
        response_text += f"[View on Google Play]({details['url']}) 📲\n\n"

        # Add histogram information
        histogram = details.get("histogram", [])
        if histogram:
            response_text += "**Ratings Breakdown:** 📊\n"
            stars = 5
            for count in histogram[::-1]:
                response_text += f"{stars}⭐: {count} 🧑‍🤝‍🧑\n"
                stars -= 1
        
        await message.edit_text(response_text)
    except Exception as e:
        await message.edit_text(f"An error occurred: {e} ❌")



modules_help["currency"] = {
    "gapp [package name ]*": " play store app search like .gapk org.thunderdog.challegram",
    
}
