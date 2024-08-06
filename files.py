import os
from time import perf_counter
import aiofiles
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# In-memory storage for file lists
bot_data = {
    'file_lists': {}
}

# Allowed directories for safety
allowed_directories = [".", "/home/user"]

# Default max file size in bytes (1MB)
default_max_file_size = 1_000_000

def is_allowed_directory(directory):
    absolute_directory = os.path.abspath(directory)
    return any(absolute_directory.startswith(os.path.abspath(allowed)) for allowed in allowed_directories)

@Client.on_message(filters.command("files", prefix) & filters.me)
async def list_files(_, message: Message):
    directory = message.text.split(maxsplit=1)[1].strip() if len(message.command) > 1 else "."

    if not os.path.isdir(directory):
        return await message.edit(f"<b>Invalid directory:</b>\n<code>{directory}</code>")

    if not is_allowed_directory(directory):
        return await message.edit(f"<b>Access to this directory is restricted:</b>\n<code>{directory}</code>")

    try:
        start_time = perf_counter()  # Start performance counter
        files = os.listdir(directory)
        files.sort()  # Sort files alphabetically
        stop_time = perf_counter()  # Stop performance counter

        file_list = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(files)) if files else "<b>No files found.</b>"
        elapsed_time = round(stop_time - start_time, 5)
        text = f"<b>Files and folders in directory:</b>\n<pre>{file_list}</pre>"
        text += f"<b>Completed in {elapsed_time} seconds.</b>"

        await message.edit(text)
        # Store the file list for later retrieval using chat ID
        bot_data['file_lists'][message.chat.id] = (directory, files)
    except Exception as e:
        await message.edit(f"<b>Error:</b>\n<code>{str(e)}</code>")

@Client.on_message(filters.reply & filters.me)
async def open_file(_, message: Message):
    if not message.reply_to_message:
        return

    # Check if the reply is related to the file list
    if message.reply_to_message.text and "Files and folders in directory:" not in message.reply_to_message.text:
        return

    # Retrieve the file list from stored data
    directory, files = bot_data['file_lists'].get(message.chat.id, (None, None))
    if directory is None or files is None:
        return await message.reply("<b>No file list available for this chat.</b>")

    try:
        reply_text = message.text.strip().split()
        command = reply_text[0].lower()

        if command.isdigit():
            index = int(command) - 1
            if 0 <= index < len(files):
                file_path = os.path.join(directory, files[index])

                if os.path.isfile(file_path):
                    if os.path.getsize(file_path) > default_max_file_size:
                        return await message.reply_to_message.edit("<b>File is too large to read or upload.</b>")

                    async with aiofiles.open(file_path, 'r') as f:
                        file_content = await f.read()
                    text = f"<b>Content of {files[index]}:</b>\n<pre>{file_content}</pre>"
                    await message.reply_to_message.edit(text)

                elif os.path.isdir(file_path):
                    files = os.listdir(file_path)
                    files.sort()  # Sort files alphabetically
                    file_list = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(files)) if files else "<b>No files found.</b>"
                    text = f"<b>Files and folders in directory:</b>\n<pre>{file_list}</pre>"
                    await message.reply_to_message.edit(text)
                    # Update the file list to the new directory
                    bot_data['file_lists'][message.chat.id] = (file_path, files)
                else:
                    await message.reply_to_message.edit(f"<b>{files[index]} is not a file or directory.</b>")
            else:
                await message.reply_to_message.edit("<b>Invalid number. Please reply with a valid number.</b>")

        elif command == "back":
            parent_directory = os.path.dirname(directory)
            if parent_directory == directory or not is_allowed_directory(parent_directory):
                return await message.reply_to_message.edit("<b>Already at the root directory or access restricted.</b>")

            try:
                files = os.listdir(parent_directory)
                files.sort()  # Sort files alphabetically
                file_list = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(files)) if files else "<b>No files found.</b>"
                text = f"<b>Files and folders in directory:</b>\n<pre>{file_list}</pre>"
                await message.reply_to_message.edit(text)
                bot_data['file_lists'][message.chat.id] = (parent_directory, files)
            except Exception as e:
                await message.reply_to_message.edit(f"<b>Error:</b>\n<code>{str(e)}</code>")

        elif command == "upload":
            if len(reply_text) < 2 or not reply_text[1].isdigit():
                return await message.reply_to_message.edit("<b>Invalid command. Example: upload 1</b>")

            index = int(reply_text[1]) - 1
            if 0 <= index < len(files):
                file_path = os.path.join(directory, files[index])
                if os.path.isfile(file_path):
                    await message.reply_document(file_path)
                else:
                    await message.reply_to_message.edit(f"<b>{files[index]} is not a file.</b>")
            else:
                await message.reply_to_message.edit("<b>Invalid number. Please reply with a valid number.</b>")

        elif command == "rename":
            if len(reply_text) < 3 or not reply_text[1].isdigit():
                return await message.reply_to_message.edit("<b>Invalid command. Example: rename 1 new_name.txt</b>")

            index = int(reply_text[1]) - 1
            new_name = reply_text[2]
            if 0 <= index < len(files):
                old_path = os.path.join(directory, files[index])
                new_path = os.path.join(directory, new_name)
                os.rename(old_path, new_path)
                await message.reply_to_message.edit(f"<b>Renamed {files[index]} to {new_name}</b>")
            else:
                await message.reply_to_message.edit("<b>Invalid number. Please reply with a valid number.</b>")

        elif command == "delete":
            if len(reply_text) < 2 or not reply_text[1].isdigit():
                return await message.reply_to_message.edit("<b>Invalid command. Example: delete 1</b>")

            index = int(reply_text[1]) - 1
            if 0 <= index < len(files):
                file_path = os.path.join(directory, files[index])
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    await message.reply_to_message.edit(f"<b>Deleted {files[index]}</b>")
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
                    await message.reply_to_message.edit(f"<b>Deleted directory {files[index]}</b>")
                else:
                    await message.reply_to_message.edit(f"<b>{files[index]} is not a file or directory.</b>")
            else:
                await message.reply_to_message.edit("<b>Invalid number. Please reply with a valid number.</b>")

        else:
            await message.reply_to_message.edit("<b>Reply with a number to open a file or directory, 'upload' to upload a file, 'rename' to rename a file, 'delete' to delete a file, or 'back' to navigate to the parent directory.</b>")

        await message.delete()
    except Exception as e:
        await message.reply_to_message.edit(f"<b>Error:</b>\n<code>{str(e)}</code>")
        await message.delete()

modules_help["files"] = {
    "files [directory]*": "List files in the specified directory (default is current directory). Example: `files /home/user`",
    "upload [number]*": "Upload the file with the specified number to Telegram. Example: `upload 1`",
    "rename [number] [new_name]*": "Rename the file with the specified number to the new name. Example: `rename 1 new_name.txt`",
    "delete [number]*": "Delete the file or directory with the specified number. Example: `delete 1`",
    "back": "Navigate to the parent directory."
                  }
                  
