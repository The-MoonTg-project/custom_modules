import os
import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix




# Define the async get_url function
async def get_url(link):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            return str(resp.url)  # Ensure it returns a string URL

@Client.on_message(filters.command("gitdl", prefix) & filters.me)
async def download_repo(client, message: Message):
    # Extract URL from the message
    url = message.text.split(" ", 1)[-1].strip()

    # Validate GitHub URL
    if not url.startswith("https://github.com/"):
        await message.reply_text("❌ Invalid URL. Please send a valid GitHub repository link. 🔗")
        return

    # Parse the URL to extract the owner and repo name
    parts = url.rstrip("/").split("/")
    if len(parts) < 5:
        await message.reply_text("❌ Invalid repository link. Please ensure it follows the format:\n`https://github.com/owner/repo` 📝")
        return

    owner, repo = parts[3], parts[4]

    # Use GitHub API to determine the default branch
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        default_branch = "main"
        
        # Fetch the default branch using the custom get_url function
        resolved_api_url = await get_url(api_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(resolved_api_url) as api_response:
                if api_response.status != 200:
                    await message.reply_text("❌ Repository not found or API error. 🛑")
                    return
                
                # Parse JSON response
                repo_data = await api_response.json()
                default_branch = repo_data.get("default_branch", "main")  # Fallback to "main" if not found

        # Construct ZIP URL
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{default_branch}.zip"

        # Download the ZIP file
        async with aiohttp.ClientSession() as session:
            async with session.get(zip_url) as response:
                if response.status == 404:
                    await message.reply_text("❌ Unable to fetch the repository ZIP. Please check the repository. 📦")
                    return

                # Save ZIP file temporarily
                zip_path = f"{repo}.zip"
                with open(zip_path, "wb") as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

        # Send the ZIP file to the user
        await message.reply_document(zip_path, caption=f"✅ Here is your ZIP file for `{repo}`! 📂")

    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {e} 🔧")

    finally:
        # Clean up the temporary file
        if os.path.exists(zip_path):
            os.remove(zip_path)



modules_help["gitdl"] = {
    "gitdl": "download GitHub repo",
}
