# copyright by https/t.me/shado_hackers

from pyrogram import Client, filters
from pyrogram.types import Message


import os
from datetime import datetime

from utils.scripts import format_exc, import_library
from utils.misc import modules_help, prefix


import_library("gtts")
import_library("lxml_html_clean")
import_library("newspaper", "newspaper3k")
nltk = import_library("nltk")
from newspaper import Article
from newspaper.article import ArticleException
from gtts import gTTS

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


# Initialize the bot

# Function to extract article text and metadata using newspaper3k
def fetch_article_metadata(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        # Extract metadata
        title = article.title if article.title else "No title"
        authors = ', '.join(article.authors) if article.authors else "Unknown author(s)"
        publish_date = article.publish_date.strftime("%Y-%m-%d") if article.publish_date else "Unknown publish date"
        text = article.text

        return {
            "title": title,
            "authors": authors,
            "publish_date": publish_date,
            "text": text
        }
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None

# Function to convert text to speech and save as audio file
def text_to_speech(text, file_name="generated_article.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(file_name)
    return file_name


@Client.on_message(filters.command("read", prefix) & filters.me)
async def read_article(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a URL after the {prefix}read command.")
        return

    url = message.command[1]
    await message.reply_text("Fetching the article...")

    # Fetch the article metadata and text using newspaper3k
    article_data = fetch_article_metadata(url)
    if not article_data:
        await message.reply_text("Failed to fetch the article.")
        return

    # Extract the article metadata
    title = article_data['title']
    authors = article_data['authors']
    publish_date = article_data['publish_date']
    article_text = article_data['text']

    # Send the metadata as a text reply
    metadata_message = f"**Title:** {title}\n**Authors:** {authors}\n**Published on:** {publish_date}"
    await message.reply_text(metadata_message)

    # Convert the article text to speech
    await message.reply_text("Converting article to audio...")
    audio_data = text_to_speech(article_text, file_name="generated_article.mp3")

    # Check if audio data was generated, and handle sending
    if audio_data:
        # Save the audio data to a file
        audio_filename = "generated_article.mp3"
        
        # Send the generated music back to the user
        await message.reply_audio(audio_filename, title="Generated Article", performer="ArticleBot")
        
        # Cleanup after sending
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
    else:
        await message.reply_text("Failed to generate audio from the article.")






modules_help["summary"] = {
    "summary [url]": "Reply with article links, getting summary of articl"
    "read [url]": "Reply with article links, getting audio of articles"
}
    

