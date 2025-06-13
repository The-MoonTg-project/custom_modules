import json
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "content-type": "application/json",
}

async def p_paste(text, extension=None):
    url = "https://pasty.lus.pm/api/v1/pastes"
    data = {"content": text}
    try:
        r = requests.post(url, data=json.dumps(data), headers=HEADERS)
        r.raise_for_status()
        resp = r.json()
        ext = extension or "txt"
        paste_id = resp.get("id")
        if not paste_id:
            return {"error": "No paste ID returned"}
        return {
            "url": f"https://pasty.lus.pm/{paste_id}.{ext}",
            "raw": f"https://pasty.lus.pm/{paste_id}/raw",
            "bin": "Pasty",
        }
    except Exception as e:
        return {"error": str(e)}

async def spacebin_paste(text, extension="txt"):
    url = "https://spaceb.in/api/"
    try:
        data = {"content": text}
        files = {"extension": (None, extension)}
        r = requests.post(url, data=data, files=files)
        r.raise_for_status()
        result = r.json()
        if result.get("error"):
            return {"error": result["error"]}
        payload = result.get("payload", {})
        paste_id = payload.get("id")
        if not paste_id:
            return {"error": "No paste ID returned"}
        return {
            "url": f"https://spaceb.in/{paste_id}",
            "raw": f"https://spaceb.in/{paste_id}/raw",
            "bin": "Spacebin",
        }
    except Exception as e:
        return {"error": str(e)}

async def get_text_from_message(message):
    reply = message.reply_to_message
    if reply:
        text = reply.text or reply.caption
        if not text and reply.document:
            try:
                doc = await reply.download()
                with open(doc, "r") as f:
                    text = f.read()
            except Exception as e:
                return None, f"<b>Error reading document: {e}</b>"
    else:
        args = message.text.split(maxsplit=1)
        text = args[1] if len(args) > 1 else ""
    if not text:
        return None, "<b>No text found to paste</b>"
    return text, None

async def handle_paste(message, service):
    args = message.text.split(maxsplit=2)
    extension = None
    if len(args) >= 2 and "." in args[1]:
        extension = args[1].split(".", 1)[1]
    text, error = await get_text_from_message(message)
    if error:
        await message.edit(error)
        return
    if service == "pasty":
        result = await p_paste(text, extension)
    else:
        result = await spacebin_paste(text, extension or "txt")
    if "error" in result:
        await message.edit(f"<b>Error: {result['error']}</b>")
    else:
        await message.edit(
            f"<b>Pasted to {result['bin']}:\n"
            f"• <a href='{result['url']}'>Link</a>\n"
            f"• <a href='{result['raw']}'>Raw</a></b>",
            disable_web_page_preview=True,
        )

@Client.on_message(filters.command("pasty", prefix) & filters.me)
async def pasty_cmd(_, message: Message):
    await handle_paste(message, "pasty")

@Client.on_message(filters.command("spacebin", prefix) & filters.me)
async def spacebin_cmd(_, message: Message):
    await handle_paste(message, "spacebin")

modules_help["pasty"] = {
    "pasty [.ext] [text/reply]": "Paste to pasty.lus.pm (default ext: txt)",
    "spacebin [.ext] [text/reply]": "Paste to spaceb.in (default ext: txt)",
}
