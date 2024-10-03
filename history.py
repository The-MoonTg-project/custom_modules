import requests
from pyrogram import Client, filters
from datetime import datetime
from utils.misc import modules_help, prefix


# Function to fetch history data from Muffinlabs API
import os
from pyrogram.errors import MessageTooLong

def get_history_data():
    today = datetime.now().strftime("%m/%d")
    url = f"http://history.muffinlabs.com/date"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        return None

def format_history(data):
    events = data.get('Events', [])
    if not events:
        return "No events found for today."
    
    formatted_events = []
    for event in events:
        year = event.get("year", "Unknown year")
        text = event.get("text", "")
        links = event.get("links", [])
        link_text = ""
        
        # Add the first link if available
        if links:
            link_title = links[0].get("title", "")
            link_url = links[0].get("link", "")
            link_text = f"\nRead more: [{link_title}]({link_url})"
        
        formatted_events.append(f"{year}: {text}{link_text}")
    
    return "\n\n".join(formatted_events)

@Client.on_message(filters.command("history", prefix) & filters.me)
async def today_history(client, message):
    try:
        # Fetch the history data
        history_data = get_history_data()
        
        if history_data:
            # Format and send the events
            events_text = format_history(history_data)
            await message.reply(events_text, disable_web_page_preview=True)
        else:
            await message.reply("Sorry, I couldn't fetch today's history data.")
    
    except MessageTooLong:
        # Save the large response to a file
        with open("history.txt", "w") as f:
            f.write(events_text)
        
        # Prepare general details for the caption
        general_details = "Here's today's historical events."
        
        # Send the file with a caption
        await message.reply_document(
            "history.txt",
            caption=f"<u><b>General Details</b></u>:\n{general_details}",
        )
        
        # Clean up by removing the file after sending
        os.remove("history.txt")
    
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
      

modules_help["history"] = {
    "history": "get the today history"
}
