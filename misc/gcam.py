import feedparser
from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup
from requests import get
from utils.misc import modules_help, prefix
from utils.scripts import import_library

bs4 = import_library("bs4", "beautifulsoup4")
feedparser = import_library("feedparser", "feedparser")

# GCam Feed URL
GCAM_FEED_URL = "https://www.celsoazevedo.com/files/android/google-camera/dev-feed.xml"

def fetch_gcam_links(limit=10):
    """Fetch GCam developer links from the XML feed."""
    feed = feedparser.parse(GCAM_FEED_URL)
    results = []
    for entry in feed.entries[:limit]:  # Limit the results
        title = entry.get("title", "No title")
        link = entry.get("link", "No link")
        results.append(f"**{title}**\n🔗 [Download]({link})")
    return results

@Client.on_message(filters.command("gcam", prefix) & filters.me)
async def gcam_search(_, message):
    """Handle .gcam command."""
    await message.reply_text("Fetching the latest GCam updates, please wait...")
    gcam_links = fetch_gcam_links(limit=10)  # Fetch only the first 10 entries
    if gcam_links:
        response = "\n\n".join(gcam_links)  # Combine results
        await message.reply_text(response, disable_web_page_preview=True)
    else:
        await message.reply_text("No updates found at the moment.")


modules_help["gcam"] = {
    "gcam": "search gcam",
    
}
