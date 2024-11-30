import requests
import os

from bs4 import BeautifulSoup

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix


def get_headers():
    """
    Returns a dictionary of headers to mimic a real browser.
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


async def scrape_site(url):
    # Make a GET request to the URL
    headers = get_headers()
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4xx or 5xx
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        return None
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        return None
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    # Find the element with the specified class
    target_element = soup.find(
        "div", class_="SimilarSitesCards__SimilarSitesCardsWrapper-hn4rvg-0 jSddga"
    )
    target_element2 = soup.find(
        "div", class_="SiteHeader__MetricsWrapper-sc-1ybnx66-10 ieoBJd"
    )
    if target_element2:
        # Extract metrics
        metrics = target_element2.find(
            "div",
            attrs={"data-testid": "siteheader_monthlyvisits"},
            class_="SiteHeader__MetricValue-sc-1ybnx66-14 cLauOv",
        ).text.strip()
        # Extract category rank
        category_rank = target_element2.find(
            "div",
            attrs={"data-testid": "siteheader_categoryrank"},
            class_="SiteHeader__MetricValue-sc-1ybnx66-14 cLauOv",
        ).text.strip()
    else:
        print("No metrics found.")
        return None
    cards_info = []
    if target_element:
        # Find all div elements with the specified data-clickgroup attribute inside the target element
        cards = target_element.find_all(
            "div", attrs={"data-clickgroup": "cardsClickGroup"}
        )
        # Extract and list the content of each card
        for card in cards:
            # Extract domain
            domain = card.find(
                "div", class_="SimilarSitesCard__Domain-zq2ozc-4 kuvZIX"
            ).text.strip()
            # Extract description
            try:
                description = card.find(
                    "div", class_="SimilarSitesCard__Description-zq2ozc-6 hvWZMH"
                ).text.strip()
            except AttributeError:
                description = card.find(
                    "div", class_="SimilarSitesCard__Description-zq2ozc-6 kxcrva"
                ).text.strip()
            # Extract similarity percentage
            similarity = card.find(
                "div", class_="SimilarSitesCard__Similarity-zq2ozc-7 dcNMfd"
            ).text.strip()
            # Append the card information to the list
            cards_info.append(
                {"Domain": domain, "Description": description, "Similarity": similarity}
            )
    else:
        cards_info = None

    return cards_info, metrics, category_rank


@Client.on_message(filters.command("similarsites", prefix) & filters.me)
async def similarsites(client: Client, message: Message):
    if len(message.command) > 1:
        target = message.text.split(maxsplit=1)[1]
    else:
        await message.edit_text(f"<code>Usage: {prefix}similarsites [domain]* </code>")
        return None
    await message.edit_text("<code>Processing your request...</code>")
    # Define the URL
    url = f"https://www.similarsites.com/site/{target}"
    try:
        cards_info, metrics, category_rank = await scrape_site(url)
    except TypeError:
        cards_info = None
        metrics = None
        category_rank = None
    except AttributeError:
        cards_info = None
        metrics = None
        category_rank = None
    mes = ""
    if cards_info is not None:
        for card in cards_info:
            mes += f"<b>Domain:</b> <code>{card['Domain']}</code>\n<b>Description:</b> <code>{card['Description']}</code>\n<b>Similarity:</b> <code>{card['Similarity']}</code>\n\n"
        await message.edit_text(
            f"<b>Target:</b> <code>{target}</code>\n<b>Category Rank:</b> <code>{category_rank}</code>\n<b>Monthly Traffic:</b> <code>{metrics}</code>\nSimilar sites:\n{mes}"
        )
    elif not cards_info:
        await message.edit_text("<code>No similar sites found.</code>")
        return None
    else:
        await message.edit_text("<code>Something went wrong.</code>")


modules_help["similarsites"] = {
    "similarsites [domain]*": "Find Similar Sites/Domains to any Sites/Domains"
}
