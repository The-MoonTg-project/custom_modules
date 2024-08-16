from pyrogram import Client, filters
import requests

from utils.misc import modules_help, prefix


def get_bug_track_info(package_info):
    # Check if a bug tracker URL is available
    bug_tracker_url = package_info.get('bugtrack_url', None)
    return bug_tracker_url if bug_tracker_url else "Not available"

def get_requirements(data):
    # Get the requires_dist field, if available
    requirements = data['info'].get('requires_dist', None)
    return "\n".join(requirements) if requirements else "Not available"




@Client.on_message(filters.command(["pypi"], prefix) & filters.me)
async def pypi_info(client, message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /pypi <package_name>")
        return

    package_name = message.command[1]

    # Fetch data from PyPI
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")

    if response.status_code == 200:
        data = response.json()
        package_info = data['info']
        
        # Prepare the response message
        reply_message = (
            f"**Package Name:** {package_info['name']}\n"
            f"**Version:** {package_info['version']}\n"
            f"**Summary:** {package_info['summary']}\n"
            f"**Home Page:** {package_info['home_page']}\n"
            f"**Author:** {package_info['author']}\n"
            f"**License:** {package_info['license']}\n"
            f"**Description:** {package_info['description']}\n"
            f"**Keywords:** {', '.join(package_info['keywords'].split()) if package_info['keywords'] else 'None'}\n"
            f"**Bug Tracker:** {get_bug_track_info(package_info)}\n"
            f"**Requirements:** {get_requirements(data)}\n"
        )

        # Add package URLs
        if 'project_urls' in package_info and package_info['project_urls']:
            reply_message += "**Project URLs:**\n"
            for label, url in package_info['project_urls'].items():
                reply_message += f"- **{label}:** {url}\n"

        await message.reply(reply_message)
    else:
        await message.reply("Package not found. Please check the package name and try again.")


modules_help["pypi"] = {
    "pypi [request]": "To get the pypi package ."
}
