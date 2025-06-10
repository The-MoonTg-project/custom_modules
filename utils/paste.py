from pyrogram import Client, filters, enums
from pyrogram.types import Message
import json
import requests
from utils.misc import modules_help, prefix

LOGS = print  # Simple logging replacement for Moon-Userbot

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "content-type": "application/json",
}

async def p_paste(message, extension=None):
    siteurl = "https://pasty.lus.pm/api/v1/pastes"
    data = {"content": message}
    try:
        response = requests.post(url=siteurl, data=json.dumps(data), headers=headers)
    except Exception as e:
        return {"error": str(e)}
    if response.ok:
        response = response.json()
        purl = (
            f"https://pasty.lus.pm/{response['id']}.{extension}"
            if extension
            else f"https://pasty.lus.pm/{response['id']}.txt"
        )
        return {
            "url": purl,
            "raw": f"https://pasty.lus.pm/{response['id']}/raw",
            "bin": "Pasty",
        }
    return {"error": "Unable to reach pasty.lus.pm"}

async def s_paste(message, extension="txt"):
    siteurl = "https://spaceb.in/api/v1/documents/"
    try:
        response = requests.post(
            siteurl, data={"content": message, "extension": extension}
        )
    except Exception as e:
        return {"error": str(e)}
    if response.ok:
        response = response.json()
        if response["error"] != "" and response["status"] < 400:
            return {"error": response["error"]}
        return {
            "url": f"https://spaceb.in/{response['payload']['id']}",
            "raw": f"{siteurl}{response['payload']['id']}/raw",
            "bin": "Spacebin",
        }
    return {"error": "Unable to reach spacebin."}

async def n_paste(message, extension=None):
    siteurl = "https://nekobin.com/api/documents"
    data = {"content": message}
    try:
        response = requests.post(url=siteurl, data=json.dumps(data), headers=headers)
    except Exception as e:
        return {"error": str(e)}
    if response.ok:
        response = response.json()
        purl = (
            f"nekobin.com/{response['result']['key']}.{extension}"
            if extension
            else f"nekobin.com/{response['result']['key']}"
        )
        return {
            "url": purl,
            "raw": f"nekobin.com/raw/{response['result']['key']}",
            "bin": "Neko",
        }
    return {"error": "Unable to reach nekobin."}

async def d_paste(message, extension=None):
    siteurl = "http://catbin.up.railway.app/documents"
    data = {"content": message}
    try:
        response = requests.post(url=siteurl, data=json.dumps(data), headers=headers)
    except Exception as e:
        return {"error": str(e)}
    if response.ok:
        response = response.json()
        purl = (
            f"http://catbin.up.railway.app/{response['key']}.{extension}"
            if extension
            else f"http://catbin.up.railway.app/{response['key']}"
        )
        return {
            "url": purl,
            "raw": f"http://catbin.up.railway.app/raw/{response['key']}",
            "bin": "Dog",
        }
    return {"error": "Unable to reach dogbin."}

async def pastetext(text_to_print, pastetype=None, extension=None):
    response = {"error": "something went wrong"}
    if pastetype is not None:
        if pastetype == "p":
            response = await p_paste(text_to_print, extension)
        elif pastetype == "s" and extension:
            response = await s_paste(text_to_print, extension)
        elif pastetype == "s":
            response = await s_paste(text_to_print)
        elif pastetype == "d":
            response = await d_paste(text_to_print, extension)
        elif pastetype == "n":
            response = await n_paste(text_to_print, extension)
    if "error" in response:
        response = await p_paste(text_to_print, extension)
    if "error" in response:
        response = await n_paste(text_to_print, extension)
    if "error" in response:
        if extension:
            response = await s_paste(text_to_print, extension)
        else:
            response = await s_paste(text_to_print)
    if "error" in response:
        response = await d_paste(text_to_print, extension)
    return response

@Client.on_message(filters.command("paste", prefix) & filters.me)
async def paste_cmd(client: Client, message: Message):
    """Paste text to various pastebin services"""
    reply = message.reply_to_message
    args = message.text.split(maxsplit=2)
    
    if len(args) < 2 and not reply:
        await message.edit("<b>Please provide text or reply to a message</b>", parse_mode=enums.ParseMode.HTML)
        return
    
    pastetype = None
    extension = None
    
    if len(args) >= 2:
        if args[1].startswith(("p", "s", "n", "d")):
            pastetype = args[1][0]
            if "." in args[1]:
                extension = args[1].split(".", 1)[1]
    
    text = ""
    if reply:
        if reply.text:
            text = reply.text
        elif reply.caption:
            text = reply.caption
        elif reply.document:
            try:
                doc = await reply.download()
                with open(doc, "r") as f:
                    text = f.read()
            except Exception as e:
                await message.edit(f"<b>Error reading document: {e}</b>", parse_mode=enums.ParseMode.HTML)
                return
    else:
        text = args[-1]
    
    if not text:
        await message.edit("<b>No text found to paste</b>", parse_mode=enums.ParseMode.HTML)
        return
    
    result = await pastetext(text, pastetype, extension)
    
    if "error" in result:
        await message.edit(f"<b>Error: {result['error']}</b>", parse_mode=enums.ParseMode.HTML)
    else:
        await message.edit(
            f"<b>Pasted to {result['bin']}:\n"
            f"• <a href='{result['url']}'>Link</a>\n"
            f"• <a href='{result['raw']}'>Raw</a></b>",
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

modules_help["paste"] = {
    "paste [p/s/n/d][.ext] [text/reply]": "Paste text to various pastebin services\n"
    "p = pasty, s = spacebin, n = nekobin, d = dogbin\n"
    "Example: .paste p.py (for python syntax highlighting)"
}
