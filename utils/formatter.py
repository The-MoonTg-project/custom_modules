from pyrogram import Client, filters, enums
from pyrogram.types import Message
from textwrap import dedent

from utils.misc import modules_help, prefix

@Client.on_message(filters.command("quote", prefix) & filters.me)
async def quote_message(client: Client, message: Message):
    if message.reply_to_message:
        quoted = message.reply_to_message
        text = quoted.text or quoted.caption or ""
        quote_text = f"❝ {text} ❞"
        if len(message.command) > 1:
            quote_text += f"\n\n— {message.command[1]}"
        await message.edit(quote_text)
    else:
        await message.edit(f"Reply to a message to quote it.\nUsage: `{prefix}quote [author]`")

@Client.on_message(filters.command("spoiler", prefix) & filters.me)
async def spoiler_text(client: Client, message: Message):
    if len(message.command) > 1:
        text = " ".join(message.command[1:])
        spoiler_text = f"<spoiler>{text}</spoiler>"
        await message.edit(spoiler_text, parse_mode=enums.ParseMode.HTML)
    else:
        await message.edit(f"Usage: `{prefix}spoiler <text>`")

@Client.on_message(filters.command("mono", prefix) & filters.me)
async def mono_text(client: Client, message: Message):
    if len(message.command) > 1:
        text = " ".join(message.command[1:])
        mono_text = f"<code>{text}</code>"
        await message.edit(mono_text, parse_mode=enums.ParseMode.HTML)
    else:
        await message.edit(f"Usage: `{prefix}mono <text>`")

@Client.on_message(filters.command("code", prefix) & filters.me)
async def code_format(client: Client, message: Message):
    if message.reply_to_message:
        code_text = message.reply_to_message.text or message.reply_to_message.caption or ""
        if len(message.command) > 1:
            language = message.command[1]
            formatted_code = f"<pre language=\"{language}\">\n{code_text}\n</pre>"
        else:
            formatted_code = f"<pre>\n{code_text}\n</pre>"
        await message.edit(formatted_code, parse_mode=enums.ParseMode.HTML)
    elif len(message.command) > 2:
        language = message.command[1]
        code_text = " ".join(message.command[2:])
        formatted_code = f"<pre language=\"{language}\">\n{code_text}\n</pre>"
        await message.edit(formatted_code, parse_mode=enums.ParseMode.HTML)
    else:
        usage = dedent(f"""
        Usage:
        Reply to a message: `{prefix}code [language]`
        Or type directly: `{prefix}code <language> <text>`
        Example: `{prefix}code python print('Hello World')`
        """)
        await message.edit(usage)

modules_help["formatter"] = {
    "quote [author]": "Quote a replied message (optional: with author)",
    "spoiler <text>": "Create spoiler text (hidden until clicked)",
    "mono <text>": "Format text as monospace",
    "code [language] <text>": "Format text as code block with optional syntax highlighting",
}
