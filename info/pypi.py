from pyrogram import Client, filters
import requests

from utils.misc import modules_help, prefix


def get_bug_track_info(package_info):
    """
    Retrieves the bug tracker URL from package info.

    Args:
        package_info (dict): Package information from PyPI.

    Returns:
        str: Bug tracker URL or "Not available" if none found.
    """
    bug_tracker_url = package_info.get("bugtrack_url", None)
    return bug_tracker_url if bug_tracker_url else "Not available"


def get_requirements(data):
    """
    Retrieves the requirements for the package.

    Args:
        data (dict): Package data from PyPI.

    Returns:
        str: Requirements list or "Not available" if none found.
    """
    requirements = data["info"].get("requires_dist", None)
    return "<br>".join(requirements) if requirements else "Not available"


@Client.on_message(filters.command("pypi", prefix) & filters.me)
async def pypi_info(_, message):
    """
    Fetches and displays information about a PyPI package.

    Args:
        client: Pyrogram client instance.
        message: Message object triggered by the command.

    Returns:
        None
    """
    if len(message.command) != 2:
        await message.edit_text(f"Usage: {prefix}pypi [package name]")
        return

    package_name = message.command[1]

    # Fetch data from PyPI
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")

    if response.status_code == 200:
        data = response.json()
        package_info = data["info"]

        reply_message = (
            f"<b>Package Information:</b>\n"
            f"<b>Package Name:</b> {package_info['name']}\n"
            f"<b>Version:</b> {package_info['version']}\n"
            f"<b>Summary:</b> {package_info['summary']}\n"
            f"<b>Home Page:</b> <a href='{package_info['home_page']}'>{package_info['home_page']}</a>\n"
            f"<b>Author:</b> {package_info['author']}\n"
            f"<b>License:</b> {package_info['license']}\n"
            f"<b>Description:</b> {package_info['description']}\n"
            f"<b>Keywords:</b> {', '.join(package_info['keywords'].split()) if package_info['keywords'] else 'None'}\n"
            f"<b>Bug Tracker:</b> {get_bug_track_info(package_info)}\n"
            f"<b>Requirements:</b> {get_requirements(data)}\n"
        )
        # Add package URLs
        if "project_urls" in package_info and package_info["project_urls"]:
            reply_message += "<b>Project URLs:</b>\n"
            for label, url in package_info["project_urls"].items():
                reply_message += f"- <b>{label}:</b> <a href='{url}'>{url}</a>\n"

        await message.edit_text(reply_message)
    else:
        await message.edit_text(
            "Package not found. Please check the package name and try again."
        )


modules_help["pypi"] = {"pypi [request]": "To get the pypi package ."}
