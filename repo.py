from pyrogram import Client, filters, enums
from pyrogram.types import Message
import re
import os
import requests

from utils.misc import modules_help, prefix

@Client.on_message(filters.command(["repo", "rp"]))
async def github_repo(client: Client, message: Message):
    try:
        if len(message.command) > 1:
            repo_input = message.command[1]
        elif message.reply_to_message:
            repo_input = message.reply_to_message.text
        else:
            await message.edit(f"<b>Usage: </b><code>{prefix}repo [link/reply to link]</code>", parse_mode=enums.ParseMode.HTML)
            return
        user, repo = None, None
        match = re.search(r'github\.com(?:/|:)([\w.-]+)/([\w.-]+)(?:\.git)?', repo_input)
        if match:
            user, repo = match.groups()
        elif '/' in repo_input:
            user, repo = repo_input.split('/')

        if not user or not repo:
            await message.edit("Could not parse the repository reference. Please provide a valid format.")
            return

        api_url = f"https://api.github.com/repos/{user}/{repo}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            repo_details = response.json()
            description = repo_details.get('description', 'No description')
            await message.edit(f"<b>Downloading Repository....\n\nRepository Name: {repo_details['name']}\nDescription: {description}</b>")
            
            default_branch = repo_details.get('default_branch', 'main')
        else:
            await message.edit("Failed to fetch repository details")
            return

        download_url = f"https://codeload.github.com/{user}/{repo}/zip/{default_branch}"
        response = requests.get(download_url, headers=headers, allow_redirects=True)

        if response.status_code == 200:
            file_name = f"{repo}-{default_branch}.zip"
            with open(file_name, 'wb') as file:
                file.write(response.content)
            await message.reply_document(document=file_name, caption= f"<b>Repository Name:</b> <a href='{repo_input}'>{repo_details['name']}</a>\n\n<b>Description:</b> <blockquote>{description}</blockquote>", parse_mode=enums.ParseMode.HTML)
            await message.delete()
            os.remove(file_name)                  
        else:
            await message.edit(f"Failed to download repository. HTTP Status: {response.status_code}")
            return

    except Exception as e:
        await message.edit(
            f"<code>[{getattr(e, 'error_code', '')}: {getattr(e, 'error_details', '')}] - {e}</code>"
        )

modules_help["repo"] = {
    "repo [link/reply to link]*": "Download GitHub repository",
}
