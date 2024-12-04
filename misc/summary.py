# copyright by https/t.me/shado_hackers

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.scripts import format_exc, import_library
from utils.misc import modules_help, prefix

import_library("lxml_html_clean")
import_library("newspaper", "newspaper3k")
nltk = import_library("nltk")
from newspaper import Article
from newspaper.article import ArticleException


nltk.download("all")


@Client.on_message(filters.command("summary", prefix) & filters.me)
async def summarize_article(_, message: Message):
    """
    Summarize an article from a given URL.

    Args:
        client (Client): Pyrogram client instance.
        message (Message): Incoming message.

    Returns:
        None
    """
    # Extract the URL from the message text (removing the command part)
    url = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if not url:
        await message.edit_text("Please provide a valid URL after the command.")
        return

    try:
        # Extract and summarize the article
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # Uses NLP to analyze the article

        response = f"""
        <b>Article Summary</b>
        <b>Title:</b> <code>{article.title}</code>
        <b>Authors:</b> <code>{', '.join(article.authors) if article.authors else 'N/A'}</code>
        <b>Summary:</b>
        <pre>{article.summary}</pre>
        """
        await message.edit_text(response)
    except ArticleException:
        return await message.edit_text(
            "Unable to extract information from the provided URL."
        )

    except Exception as e:
        return await message.edit_text(f"An error occurred: {format_exc(e)}")


modules_help["summary"] = {
    "summary [url]": "Reply with article links, getting summary of articles"
}
