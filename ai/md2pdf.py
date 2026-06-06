import os

from pyrogram import Client, filters
from pyrogram.types import Message
from utils.scripts import import_library

from utils import modules_help, prefix

import_library("markdown_pdf", "markdown-pdf")

from markdown_pdf import MarkdownPdf, Section

@Client.on_message(filters.command("md2pdf", prefix) & filters.me)
async def md2pdf_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("Reply to a markdown file")
        return
    if not message.reply_to_message.document:
        await message.edit("Reply to a markdown file")
        return
    
    file_name = message.reply_to_message.document.file_name
    if not file_name or not (file_name.endswith(".md") or file_name.endswith(".txt")):
        await message.edit("Reply to a .md or .txt file")
        return
        
    await message.edit("Downloading file...")
    md_file = await message.reply_to_message.download()
    
    await message.edit("Converting to PDF...")
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        pdf_name = f"{file_name.rsplit('.', 1)[0]}.pdf"
        
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(content))
        pdf.save(pdf_name)
        
        await message.edit("Uploading PDF...")
        await client.send_document(
            message.chat.id,
            document=pdf_name,
            file_name=pdf_name,
            reply_to_message_id=message.reply_to_message.id,
        )
        await message.delete()
        os.remove(pdf_name)
    except Exception as e:
        await message.edit(f"Error: {e}")
    finally:
        if os.path.exists(md_file):
            os.remove(md_file)

modules_help["md2pdf"] = {"md2pdf": "Convert a markdown file to pdf"}
