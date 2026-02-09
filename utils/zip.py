import os
import zipfile
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
import asyncio


TMP_DOWNLOAD_DIRECTORY = "./downloads/"
extracted = os.path.join(TMP_DOWNLOAD_DIRECTORY, "extracted/")


os.makedirs(TMP_DOWNLOAD_DIRECTORY, exist_ok=True)
os.makedirs(extracted, exist_ok=True)


@Client.on_message(filters.command("zip", prefix) & filters.me)
async def zip_cmd(client: Client, message: Message):
    
    if not message.reply_to_message:
        await message.edit("**Please reply to a file to compress.**")
        return
    
    await message.edit("**Processing...**")
    
    try:
        # File download
        file_path = await message.reply_to_message.download(
            file_name=TMP_DOWNLOAD_DIRECTORY
        )
        
        # Zip file create
        zip_path = f"{file_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, os.path.basename(file_path))
        
        # Zip file send
        await client.send_document(
            chat_id=message.chat.id,
            document=zip_path,
            caption="**Zipped!**",
            reply_to_message_id=message.reply_to_message.id
        )
        
        # Temporary files delete
        os.remove(file_path)
        os.remove(zip_path)
        await message.delete()
        
    except Exception as e:
        await message.edit(f"**Error:** `{str(e)}`")


@Client.on_message(filters.command("unzip", prefix) & filters.me)
async def unzip_cmd(client: Client, message: Message):
    
    if not message.reply_to_message:
        await message.edit("**Please reply to a zip file to extract.**")
        return
    
    if not message.reply_to_message.document:
        await message.edit("**Please reply to a zip file.**")
        return
    
    start_time = datetime.now()
    await message.edit("**Processing...**")
    
    try:
        # Zip file download
        zip_path = await message.reply_to_message.download(
            file_name=TMP_DOWNLOAD_DIRECTORY
        )
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted)
        
        # Extracted files list
        extracted_files = []
        for root, dirs, files in os.walk(extracted):
            for file in files:
                extracted_files.append(os.path.join(root, file))
        
        
        for file_path in extracted_files:
            try:
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_path,
                    caption=f"**Unzipped:** `{os.path.basename(file_path)}`",
                    reply_to_message_id=message.id
                )
                os.remove(file_path)
            except Exception as e:
                await message.reply(f"**Error sending {os.path.basename(file_path)}:** `{str(e)}`")
        
        # Cleanup
        os.remove(zip_path)
        
        # Remove empty directories
        for root, dirs, files in os.walk(extracted, topdown=False):
            for dir_name in dirs:
                try:
                    os.rmdir(os.path.join(root, dir_name))
                except:
                    pass
        
        end_time = datetime.now()
        time_taken = (end_time - start_time).seconds
        await message.edit(f"**Unzipping completed in {time_taken} seconds!**")
        
    except zipfile.BadZipFile:
        await message.edit("**Error: Invalid zip file.**")
    except Exception as e:
        await message.edit(f"**Error:** `{str(e)}`")


# Module help text
modules_help["zip_unzip"] = {
    "zip [reply to file]": "Compress a file into zip format",
    "unzip [reply to zip file]": "Extract files from a zip archive"
}
