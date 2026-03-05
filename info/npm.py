import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix


async def search_npm_packages(query):
    url = f"https://registry.npmjs.org/-/v1/search?text={query}&size=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("objects", [])
    return []


# Function to format package info
def format_package_info(package):
    pkg = package["package"]
    name = pkg["name"]
    version = pkg["version"]
    description = pkg.get("description", "No description available")
    link = pkg["links"]["npm"]

    # Additional details
    author = pkg.get("author", {}).get("name", "Unknown")
    email = pkg.get("author", {}).get("email", "No email available")
    maintainers = pkg.get("maintainers", [])
    maintainer_list = "\n".join(
        f"Username: {m['username']}, Email: {m['email']}" for m in maintainers
    )

    return (
        f"**{name}**\n"
        f"Version: {version}\n"
        f"Description: {description}\n"
        f"Author: {author}\n"
        f"Email: {email}\n"
        f"Maintainers:\n{maintainer_list}\n\n"
        f"[View on npm]({link})"
    )


@Client.on_message(filters.command("npm", prefix) & filters.me)
async def npm_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: <code>{prefix}npm</code> <package_name>")
        return

    query = " ".join(message.command[1:])
    m = await message.edit_text(f"Searching for NPM packages: {query}")
    packages = await search_npm_packages(query)

    if not packages:
        await m.edit_text("No packages found.")
        return

    for package in packages:
        package_info = format_package_info(package)
        await message.reply_text(package_info, disable_web_page_preview=True)
    m.delete()


modules_help["npm"] = {"npm": "Search for NPM packages."}
