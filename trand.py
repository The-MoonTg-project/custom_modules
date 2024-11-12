from pyrogram import Client, filters
from bs4 import BeautifulSoup
import aiohttp
import random


from utils.misc import modules_help, prefix


# Function to get a random user agent (optional but recommended)
def get_ua():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        # Add more user agents if needed
    ]
    return random.choice(user_agents)

# Define the function to get trending hashtags
async def get_trendings(country: str):
    base_url = "https://getdaytrends.com"
    url = f"{base_url}/{country}"
    headers = {"user-agent": get_ua()}

    # Extract data from table
    def get_result(data):
        tags = data.table.find_all('tr')
        results = []
        for tr in tags:
            src = tr.td
            title = src.get_text()
            link = base_url + src.a.get('href')
            results.append({'title': title, 'url': link})
        return results

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {'error': response.reason}
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                tables = soup.select("div[class^='inset']")
                return {
                    'now_hashtags': get_result(tables[0]),
                    'today_hashtags': get_result(tables[1]),
                    'top_hashtags': get_result(tables[2])
                }
        except Exception as e:
            return {'error': str(e)}


# Command to get trends based on a given country
@Client.on_message(filters.command("trand", prefix) & filters.me)
async def trend_command(client, message):
    # Get the country code from the command arguments
    if len(message.command) < 2:
        await message.reply("Please specify a country code, e.g., `/trend india`.")
        return
    
    country = message.command[1].lower()
    trends = await get_trendings(country)
    
    if 'error' in trends:
        await message.reply(f"Error: {trends['error']}")
        return
    
    # Format the results
    response = f"**Trending Hashtags for {country.upper()}**\n\n"
    
    response += "**Now Trending:**\n"
    for tag in trends['now_hashtags']:
        response += f"- [{tag['title']}]({tag['url']})\n"

    response += "\n**Today Trending:**\n"
    for tag in trends['today_hashtags']:
        response += f"- [{tag['title']}]({tag['url']})\n"

    response += "\n**Top Hashtags:**\n"
    for tag in trends['top_hashtags']:
        response += f"- [{tag['title']}]({tag['url']})\n"

    await message.reply(response, disable_web_page_preview=True)



modules_help["trand"] = {
    "tranf [country]": "get latest twitter trading of a country "
}
