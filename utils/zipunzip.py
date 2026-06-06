import os
import shutil
import tarfile
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix
from utils.scripts import import_library, format_exc

# Auto-install pure Python compression libs
pyzipper = import_library("pyzipper")
py7zr = import_library("py7zr")

ZIP_TEMP_DIR = "/tmp/moonub_zip/"
EXTRACT_DIR = "/tmp/moonub_extract/"
ZIP_FILES = {}

os.makedirs(ZIP_TEMP_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

@Client.on_message(filters.command("addz", prefix) & filters.me)
async def add_file(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.edit("`Reply to a file/media to add it to the zip list.`")
        return
        
    hmm = await message.edit("`Downloading file...`")
    file_path = await message.reply_to_message.download(file_name=ZIP_TEMP_DIR)
    
    if not file_path:
        await hmm.edit("`Failed to download file.`")
        return
        
    filename = os.path.basename(file_path)
    
    # Overwrite if exists
    if filename in ZIP_FILES and ZIP_FILES[filename] != file_path:
        if os.path.exists(ZIP_FILES[filename]):
            os.remove(ZIP_FILES[filename])
            
    ZIP_FILES[filename] = file_path
    await hmm.edit(f"`Successfully added` `{filename}` `to the queue.`\nTotal files: {len(ZIP_FILES)}")

@Client.on_message(filters.command("removez", prefix) & filters.me)
async def remove_file(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("`Please provide the exact filename to remove.`")
        return
        
    filename = " ".join(message.command[1:])
    if filename in ZIP_FILES:
        if os.path.exists(ZIP_FILES[filename]):
            os.remove(ZIP_FILES[filename])
        del ZIP_FILES[filename]
        await message.edit(f"`Removed` `{filename}` `from the queue.`")
    else:
        await message.edit(f"`File` `{filename}` `not found in the queue.`")

@Client.on_message(filters.command("listz", prefix) & filters.me)
async def list_files(client: Client, message: Message):
    if not ZIP_FILES:
        await message.edit("`The queue is empty.`")
        return
        
    text = "**Files in Queue:**\n"
    for i, filename in enumerate(ZIP_FILES.keys(), 1):
        text += f"{i}. `{filename}`\n"
    
    await message.edit(text)

@Client.on_message(filters.command(["zip", "zipp", "7zip", "tar"], prefix) & filters.me)
async def create_archive(client: Client, message: Message):
    if not ZIP_FILES:
        await message.edit("`No files in the queue. Use .addz first.`")
        return
        
    cmd = message.command[0]
    text = " ".join(message.command[1:])
    
    if not text:
        await message.edit(f"`Please provide an archive name. Example:` `{prefix}{cmd} myfiles`")
        return
        
    password = None
    if "|" in text:
        archive_name, password = text.split("|", 1)
        archive_name = archive_name.strip()
        password = password.strip()
    else:
        archive_name = text.strip()
    
    hmm = await message.edit(f"`Creating {cmd} archive...`")
    
    try:
        if cmd == "tar":
            if not archive_name.endswith(".tar"):
                archive_name += ".tar"
            archive_path = os.path.join(ZIP_TEMP_DIR, archive_name)
            with tarfile.open(archive_path, "w") as tar:
                for filename, filepath in ZIP_FILES.items():
                    tar.add(filepath, arcname=filename)
                    
        elif cmd == "7zip":
            if not archive_name.endswith(".7z"):
                archive_name += ".7z"
            archive_path = os.path.join(ZIP_TEMP_DIR, archive_name)
            with py7zr.SevenZipFile(archive_path, 'w', password=password) as archive:
                for filename, filepath in ZIP_FILES.items():
                    archive.write(filepath, arcname=filename)
                    
        elif cmd in ("zip", "zipp"):
            if not archive_name.endswith(".zip"):
                archive_name += ".zip"
            archive_path = os.path.join(ZIP_TEMP_DIR, archive_name)
            
            if password:
                with pyzipper.AESZipFile(archive_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
                    zf.setpassword(password.encode('utf-8'))
                    for filename, filepath in ZIP_FILES.items():
                        zf.write(filepath, arcname=filename)
            else:
                with pyzipper.ZipFile(archive_path, 'w', pyzipper.ZIP_DEFLATED) as zf:
                    for filename, filepath in ZIP_FILES.items():
                        zf.write(filepath, arcname=filename)
                        
        await hmm.edit("`Uploading archive...`")
        await client.send_document(
            message.chat.id,
            archive_path,
            caption=f"**Archived by @moonuserbot**"
        )
        await hmm.delete()
        
        # Cleanup
        os.remove(archive_path)
        for filepath in ZIP_FILES.values():
            if os.path.exists(filepath):
                os.remove(filepath)
        ZIP_FILES.clear()
        
    except Exception as e:
        await hmm.edit(f"`Error:` {format_exc(e)}")

@Client.on_message(filters.command(["unzip", "unzipp"], prefix) & filters.me)
async def unzip_archive(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.edit("`Reply to a zip, 7z, or tar file to extract it.`")
        return
        
    text = " ".join(message.command[1:])
    password = None
    
    if "|" in text:
        text, password = text.split("|", 1)
        text = text.strip()
        password = password.strip()
        
    args = text.split() if text else []
    
    extract_all = False
    target_file = None
    
    if "-all" in args:
        extract_all = True
        args.remove("-all")
        
    if args:
        target_file = " ".join(args)
        
    hmm = await message.edit("`Downloading archive...`")
    archive_path = await message.reply_to_message.download(file_name=EXTRACT_DIR)
    
    if not archive_path:
        await hmm.edit("`Failed to download archive.`")
        return
        
    file_list = []
    is_zip = archive_path.endswith(".zip")
    is_7z = archive_path.endswith(".7z")
    is_tar = archive_path.endswith(".tar") or archive_path.endswith(".tar.gz") or archive_path.endswith(".tgz")
    
    try:
        if is_tar:
            with tarfile.open(archive_path, "r") as tar:
                file_list = tar.getnames()
        elif is_7z:
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as z:
                file_list = z.getnames()
        else: # Default to zip
            with pyzipper.AESZipFile(archive_path) as zf:
                if password:
                    zf.setpassword(password.encode('utf-8'))
                file_list = zf.namelist()
                    
        # Filter out directories
        file_list = [f for f in file_list if not f.endswith('/')]
        
    except Exception as e:
        await hmm.edit(f"`Error reading archive (invalid password?):` {e}")
        os.remove(archive_path)
        return
        
    if not file_list:
        await hmm.edit("`Archive is empty or couldn't be read.`")
        os.remove(archive_path)
        return
        
    # Mode 1: List files
    if not extract_all and not target_file:
        text = "**Archive Contents:**\n"
        for i, fname in enumerate(file_list, 1):
            text += f"{i}. `{fname}`\n"
        text += f"\nUse `{prefix}unzip -all` to extract everything, or `{prefix}unzip [index_number]` to extract a specific file."
        
        if len(text) > 4096:
            text = text[:4000] + "\n... (truncated)"
            
        await hmm.edit(text)
        os.remove(archive_path)
        return
        
    # Mode 2 & 3: Extract
    files_to_extract = file_list if extract_all else [target_file]
    
    if target_file and target_file not in file_list:
        if target_file.isdigit() and 1 <= int(target_file) <= len(file_list):
            files_to_extract = [file_list[int(target_file) - 1]]
        else:
            await hmm.edit(f"`File/Index` `{target_file}` `not found in archive.`")
            os.remove(archive_path)
            return

    await hmm.edit("`Extracting...`")
    
    ext_session_dir = os.path.join(EXTRACT_DIR, f"ext_{message.id}")
    os.makedirs(ext_session_dir, exist_ok=True)
    
    try:
        if is_tar:
            with tarfile.open(archive_path, "r") as tar:
                members = [tar.getmember(f) for f in files_to_extract]
                tar.extractall(path=ext_session_dir, members=members)
        elif is_7z:
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as z:
                z.extract(path=ext_session_dir, targets=files_to_extract)
        else:
            with pyzipper.AESZipFile(archive_path) as zf:
                if password:
                    zf.setpassword(password.encode('utf-8'))
                for f in files_to_extract:
                    zf.extract(f, path=ext_session_dir)
                    
        await hmm.edit("`Uploading extracted files...`")
        
        for f in files_to_extract:
            extracted_path = os.path.join(ext_session_dir, f)
            if os.path.exists(extracted_path) and os.path.isfile(extracted_path):
                await client.send_document(
                    message.chat.id,
                    extracted_path,
                    caption=f"**Unzipped by @moonuserbot**\n`{os.path.basename(f)}`",
                    reply_to_message_id=message.reply_to_message.id
                )
                
        await hmm.delete()
        
    except Exception as e:
        await hmm.edit(f"`Error during extraction:` {format_exc(e)}")
        
    finally:
        os.remove(archive_path)
        shutil.rmtree(ext_session_dir, ignore_errors=True)

modules_help["zipunzip"] = {
    "addz": "Reply to a file to add it to the zipping queue.",
    "removez [filename]": "Remove a specific file from the queue.",
    "listz": "List all files currently in the queue.",
    "zip [name]": "Create a zip archive from the queue.",
    "zipp [name] | [password]": "Create a password-protected zip.",
    "7zip [name]": "Create a 7z archive from the queue.",
    "tar [name]": "Create a tar archive from the queue.",
    "unzip": "Reply to an archive. Lists its contents.",
    "unzip -all | [password]": "Reply to an archive to extract everything. Optional password.",
    "unzipp [filename/index] | [password]": "Reply to an archive to extract a specific file. Same as unzip."
}
