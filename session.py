from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("session", prefix) & filters.me)
async def session(client: Client, message: Message):
    first_name = (client.get_me()).first_name
    string_session_ = f"<b><u>String Session For {first_name}</b></u> \n<code>{client.export_session_string()}</code>"
    client.send_message("me", string_session_, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
    print(f"String Has Been Sent To Your Saved Message : {first_name}")

modules_help["session"] = {
    "session": "DANGER... Use with Caution... Backup session to saved messages"
}