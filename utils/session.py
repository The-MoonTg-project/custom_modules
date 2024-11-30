from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("session", prefix) & filters.me)
async def session(client: Client, message: Message):
    b_f = await client.get_me()
    u_n = b_f.username
    await client.send_message(
        "me",
        f"<b><u>String Session For {u_n}</b></u> \n<code>{client.export_session_string()}</code>",
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await message.edit_text(f"String Has Been Sent To Your Saved Message : {u_n}")


modules_help["session"] = {
    "session": "DANGER... Use with Caution... Backup session to saved messages"
}
