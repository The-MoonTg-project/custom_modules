import os

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.scripts import format_exc

from utils import modules_help, prefix


@Client.on_message(filters.command(["repod", "rp"], prefix) & filters.me)
async def repo_download(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text(
            f"<b>Usage:</b> <code>{prefix}repo [owner/repo]</code>"
        )

    repo = message.text.split(maxsplit=1)[1]
    if "/" not in repo:
        return await message.edit_text(
            "Please provide a valid repository in the format owner/repo"
        )

    await message.edit_text(f"<code>Fetching repository info for {repo}...</code>")

    zip_filename = None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.github.com/repos/{repo}") as resp:
                if resp.status != 200:
                    return await message.edit_text(
                        f"Repository not found or API error (status {resp.status})"
                    )
                data = await resp.json()

            repo_name = data.get("name", "")
            description = data.get("description", "N/A")
            stars = data.get("stargazers_count", 0)
            forks = data.get("forks_count", 0)
            language = data.get("language", "N/A")
            default_branch = data.get("default_branch", "main")

            info = (
                f"<b>Repository:</b> <code>{data['full_name']}</code>\n"
                f"<b>Description:</b> {description}\n"
                f"<b>Stars:</b> {stars} | <b>Forks:</b> {forks}\n"
                f"<b>Language:</b> {language}\n"
                f"<b>Default Branch:</b> {default_branch}\n"
            )

            await message.edit_text(f"{info}\n<code>Downloading repository...</code>")

            zip_url = (
                f"https://github.com/{repo}/archive/refs/heads/{default_branch}.zip"
            )
            async with session.get(zip_url) as resp:
                if resp.status != 200:
                    return await message.edit_text("Failed to download repository")
                zip_data = await resp.read()

            zip_filename = f"{repo_name}-{default_branch}.zip"
            with open(zip_filename, "wb") as f:
                f.write(zip_data)

            await message.edit_text(f"{info}\n<code>Uploading...</code>")
            await client.send_document(
                message.chat.id,
                zip_filename,
                caption=info,
            )
            await message.delete()

        except Exception as e:
            await message.edit_text(format_exc(e))
        finally:
            if zip_filename and os.path.exists(zip_filename):
                os.remove(zip_filename)


modules_help["repo"] = {
    "repod [owner/repo]*": "Download a GitHub repository as a zip file",
}
