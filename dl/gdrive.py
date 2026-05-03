import os
import time
import asyncio
import tempfile
import aiohttp
import aiofiles
import mimetypes
import json

from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.scripts import format_exc, progress
from utils.db import db

AUTH_WEBSITE_URL = "https://open-authenticator.vercel.app"

UPLOAD_INIT = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"
FILES_API = "https://www.googleapis.com/drive/v3/files"

MODULE_DB = "custom.gdrive"

def _get_creds():
    return db.get(MODULE_DB, "credentials", None)


def _set_creds(c):
    db.set(MODULE_DB, "credentials", c)


def _clear_creds():
    db.remove(MODULE_DB, "credentials")


def _get_folder():
    return db.get(MODULE_DB, "folder", None)


def _set_folder(value):
    db.set(MODULE_DB, "folder", value)


def _clear_folder():
    db.remove(MODULE_DB, "folder")


def _fmt_mib(n: int) -> str:
    try:
        n = int(n)
    except Exception:
        return "0.00 MiB"
    return f"{n / (1024 * 1024):.2f} MiB"


def _progress_bar(percent: float, length: int = 10) -> str:
    try:
        p = max(0.0, min(100.0, float(percent)))
    except Exception:
        p = 0.0
    filled = int((p / 100.0) * length)
    return "▰" * filled + "▱" * (length - filled)


async def _refresh_token_if_needed(creds):
    if time.time() < creds.get("expires_at", 0) - 60:
        return creds

    refresh_token = creds.get("refresh_token")
    if not refresh_token:
        raise ValueError("No refresh token available. Please re-authenticate with .gauth")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AUTH_WEBSITE_URL}/api/auth/refresh",
                json={"refresh_token": refresh_token},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise ValueError(f"Token refresh failed: {text}")
                data = await resp.json()

        creds["access_token"] = data["access_token"]
        creds["expires_at"] = data.get("expires_at", time.time() + 3600)
        if "refresh_token" in data:
            creds["refresh_token"] = data["refresh_token"]
        
        _set_creds(creds)
        return creds
    except Exception as e:
        raise ValueError(f"Failed to refresh token: {str(e)}")


async def _get_account_info(token):
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.googleapis.com/drive/v3/about?fields=user,storageQuota",
            headers=headers
        ) as resp:
            data = await resp.json()

    user = data.get("user", {})
    quota = data.get("storageQuota", {})

    email = user.get("emailAddress", "Unknown")
    total = int(quota.get("limit", 0))
    used = int(quota.get("usage", 0))
    free = total - used if total else 0

    def fmt(x):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if x < 1024:
                return f"{x:.2f} {unit}"
            x /= 1024
        return f"{x:.2f} PB"

    return email, fmt(used), fmt(total), fmt(free)


async def _get_or_create_folder(token, folder_name):
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

        async with session.get(
            f"{FILES_API}?q={query}&fields=files(id,name)",
            headers=headers
        ) as resp:
            data = await resp.json()

        files = data.get("files", [])
        if files:
            return files[0]["id"]

        async with session.post(
            FILES_API,
            headers=headers,
            json={
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder"
            }
        ) as resp:
            data = await resp.json()
            return data.get("id")


async def _make_public(file_id, token):
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{FILES_API}/{file_id}/permissions",
            json={"role": "reader", "type": "anyone"},
            headers=headers
        )

        async with session.get(
            f"{FILES_API}/{file_id}?fields=webViewLink,webContentLink",
            headers=headers
        ) as resp:
            data = await resp.json()
            return data.get("webViewLink", ""), data.get("webContentLink", "")


async def _upload_resumable(path, name, mime, token, message):
    size = os.path.getsize(path)
    start_time = time.time()

    folder_value = _get_folder()

    if folder_value:
        if len(folder_value) > 20:
            folder_id = folder_value
        else:
            folder_id = await _get_or_create_folder(token, folder_value)
    else:
        folder_id = await _get_or_create_folder(token, "opentg")

    meta_json = {"name": name, "parents": [folder_id]}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            UPLOAD_INIT,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Upload-Content-Type": mime,
                "X-Upload-Content-Length": str(size),
                "Content-Type": "application/json"
            },
            json=meta_json
        ) as resp:
            if resp.status != 200:
                raise ValueError(await resp.text())
            upload_url = resp.headers.get("Location")

        chunk_size = 5 * 1024 * 1024
        uploaded = 0

        async with aiofiles.open(path, "rb") as f:
            while uploaded < size:
                chunk = await f.read(chunk_size)
                start = uploaded
                end = start + len(chunk) - 1

                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{end}/{size}"
                }

                for i in range(3):
                    async with session.put(upload_url, data=chunk, headers=headers) as r:
                        if r.status in (200, 201):
                            await progress(size, size, message, start_time, "<b>☁️ Uploading...</b>", name)
                            return await r.json()

                        elif r.status == 308:
                            uploaded = end + 1
                            await progress(uploaded, size, message, start_time, "<b>☁️ Uploading...</b>", name)
                            break

                        elif i == 2:
                            raise ValueError(await r.text())

                        await asyncio.sleep(2)


@Client.on_message(filters.command("gauth", prefix) & filters.me)
async def gauth_cmd(_, message: Message):
    creds = _get_creds()
    if creds:
        try:
            creds = await _refresh_token_if_needed(creds)
            email, used, total, free = await _get_account_info(creds["access_token"])

            return await message.edit(
                "✅ <b>Google Drive Connected</b>\n\n"
                f"👤 <b>Email:</b> <code>{email}</code>\n"
                f"📦 <b>Used:</b> <code>{used}</code>\n"
                f"💾 <b>Total:</b> <code>{total}</code>\n"
                f"🆓 <b>Free:</b> <code>{free}</code>\n\n"
                f"📁 <b>Folder:</b> <code>{_get_folder() or 'opentg'}</code>"
            )
        except:
            return await message.edit("⚠️ Connected but failed to fetch info.")

    auth_url = f"{AUTH_WEBSITE_URL}?mode=manual"
    await message.edit(
        "🔐 <b>Google Drive Auth</b>\n\n"
        "1. Open the link below\n"
        "2. Authenticate with Google\n"
        "3. Copy the JSON token shown\n"
        "4. Use: <code>.gtoken [paste JSON]</code>\n\n"
        f"🔗 <a href='{auth_url}'>Authenticate</a>",
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("gtoken", prefix) & filters.me)
async def gtoken_cmd(_, message: Message):
    token_str = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    
    if not token_str and message.reply_to_message:
        token_str = message.reply_to_message.text

    if not token_str:
        return await message.edit("❌ <b>Please provide the JSON string.</b>\nUsage: <code>.gtoken {json}</code>")

    try:
        data = json.loads(token_str)
        if "credentials" not in data:
            return await message.edit("❌ <b>Invalid JSON format.</b>\nEnsure you copied the entire token from the auth website.")
        
        creds = data["credentials"]
        _set_creds(creds)
        email = data.get("email", "your account")
        
        await message.edit(f"✅ <b>Google Drive successfully connected to:</b>\n<code>{email}</code>")
    except json.JSONDecodeError:
        await message.edit("❌ <b>Failed to parse JSON.</b>\nMake sure you copied the text exactly.")
    except Exception as e:
        await message.edit(f"❌ <b>Error processing token:</b> {str(e)}")


@Client.on_message(filters.command("gfolder", prefix) & filters.me)
async def gfolder_cmd(_, message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) == 1:
        return await message.edit(
            f"📁 Current folder:\n<code>{_get_folder() or 'opentg'}</code>"
        )

    val = args[1].strip()

    if val.lower() == "clear":
        _clear_folder()
        return await message.edit("✅ Reset to default (opentg)")

    _set_folder(val)
    await message.edit(f"✅ Folder set:\n<code>{val}</code>")


@Client.on_message(filters.command("gup", prefix) & filters.me)
async def gup_cmd(client: Client, message: Message):
    try:
        creds = _get_creds()
        if not creds:
            return await message.edit("❌ Use .gauth first")

        reply = message.reply_to_message
        if not reply:
            return await message.edit("❌ Reply to a file")

        media = reply.document or reply.video or reply.audio or reply.photo or reply.voice or reply.animation
        if not media:
            return await message.edit("❌ No valid file")

        file_name = getattr(media, "file_name", None) or f"file_{media.file_id[:8]}"
        start_time = time.time()

        try:
            total_bytes = getattr(media, "file_size", 0) or 0
            bar = _progress_bar(0.0)
            seed = (
                "<b>📥 Downloading...</b>\n"
                f"<b>File Name:</b> {file_name}\n"
                f"{bar}{0.00:.2f}%\n"
                f"0.0 MiB of {_fmt_mib(total_bytes)}\n"
                f"ETA: --"
            )
            message = await message.edit(seed, disable_web_page_preview=True)
        except Exception:
            pass

        with tempfile.TemporaryDirectory() as tmp:
            path = await client.download_media(
                reply,
                file_name=os.path.join(tmp, file_name),
                progress=progress,
                progress_args=(message, start_time, "<b>📥 Downloading...</b>", file_name),
            )

            mime = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            size = os.path.getsize(path)

            try:
                bar = _progress_bar(0.0)
                seed_up = (
                    "<b>☁️ Uploading...</b>\n"
                    f"<b>File Name:</b> {file_name}\n"
                    f"{bar}{0.00:.2f}%\n"
                    f"0.0 MiB of {_fmt_mib(size)}\n"
                    f"ETA: --"
                )
                message = await message.edit(seed_up, disable_web_page_preview=True)
            except Exception:
                pass

            creds = await _refresh_token_if_needed(creds)
            meta = await _upload_resumable(path, file_name, mime, creds["access_token"], message)

        file_id = meta.get("id")
        view, direct = await _make_public(file_id, creds["access_token"])

        await message.edit(
            f"✅ Uploaded\n\n📄 <code>{file_name}</code>\n📦 {round(size/1024/1024,2)} MB\n"
            f"🔗 <a href='{view}'>View</a>\n⬇️ <a href='{direct}'>Download</a>",
            disable_web_page_preview=True
        )

    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("glogout", prefix) & filters.me)
async def glogout_cmd(_, message: Message):
    _clear_creds()
    await message.edit("✅ Disconnected")


modules_help["gdrive"] = {
    "gauth": "Show auth status or get auth link",
    "gtoken [json]": "Paste the JSON token from auth website",
    "gfolder [name/id/clear]": "Set upload folder",
    "glogout": "Disconnect Google Drive",
    "gup [reply to file]": "Upload file to Drive",
}
