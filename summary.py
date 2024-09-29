#copyright by https/t.me/shado_hackers

from pyrogram import Client, filters
from newspaper import Article
import nltk
from utils.scripts import format_exc, import_library
from utils.misc import modules_help, prefix

newspaper3k = import_library("newspaper3k")

nltk = import_library("nltk")

# Download the NLTK data for tokenization

nltk.download('all')

# Article summary handler
@Client.on_message(filters.command('summary', prefix) & filters.me)
async def summarize_article(client, message):
    # Extract the URL from the message text (removing the command part)
    url = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if not url:
        await message.reply_text("Please provide a valid URL after the command.")
        return

    try:
        # Extract and summarize the article
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # Uses NLP to analyze the article
        
        # Prepare response
        title = f"**Title**: {article.title}\n"
        authors = f"**Authors**: {', '.join(article.authors)}\n" if article.authors else ""
        summary = f"**Summary**:\n{article.summary}\n"
        
        response = title + authors + summary

        # Send the article summary
        await message.reply_text(response, parse_mode=enums.ParseMode.MARKDOWN)
        
    except Exception as e:
        # Error handling for invalid URL or other issues
        await message.reply_text(f"An error occurred: {str(e)}")

modules_help["summary"] = {
    "summary [url]": " reply with artical links,getting summary of articles"
     
}
