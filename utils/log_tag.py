from datetime import datetime

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import import_library

from utils.db import db

pytz = import_library("pytz")


@Client.on_message(filters.command("log_tag_on", prefix) & filters.me)
async def log_chat(_, message: Message):
    db.set("custom.tag_logger", "tag_log", True)
    ms = await message.reply_text("Tag Log Turned ON Successfully")
    await message.delete()
    await ms.delete(5)
    return


@Client.on_message(filters.command("log_tag_off", prefix) & filters.me)
async def log_chatoff(_, message: Message):
    db.remove("custom.tag_logger", "tag_log")
    ms = await message.reply_text("Tag Log Turned Off Successfully")
    await message.delete()
    await ms.delete(5)
    return


@Client.on_message(filters.command("log_tag_chat", prefix) & filters.me)
async def log_chat(_, message: Message):
    LOG_CHAT = message.chat.id
    db.set("custom.tag_logger", "tag_log_chat", LOG_CHAT)
    ms = await message.reply_text("Tag Log Chat Updated Successfully")
    await message.delete()
    await ms.delete(5)
    return


@Client.on_message(filters.command("log_tag_chat_rm", prefix) & filters.me)
async def log_chatoff(_, message: Message):
    LOG_CHAT = message.chat.id
    db.remove("custom.tag_logger", "tag_log_chat")
    ms = await message.reply_text("Tag Log Chat Removed Successfully")
    await message.delete()
    await ms.delete(5)
    return


@Client.on_message(filters.mentioned & filters.incoming, group=-3)
async def mentioned_alert(client: Client, message: Message):
    LOG_CHAT = db.get("custom.tag_logger", "tag_log_chat")
    TAG_LOG = db.get("custom.tag_logger", "tag_log")
    if TAG_LOG:
        if LOG_CHAT is not None:
            if not message:
                return
            if not message.from_user:
                return
            chat_name = message.chat.title
            chat_id = message.chat.id
            if chat_id < 0:
                chat_id = int(str(chat_id).replace("-100", ""))
            tagged_msg_link = "https://t.me/c/{}/{}".format(chat_id, message.id)
            message_text = ""
            if message.text:
                message_text = message.text
            else:
                message_text = message.caption
            user_ = f"@{message.from_user.username}" or message.from_user.mention
            TZ = pytz.timezone("Asia/Kolkata")
            datetime_tz = datetime.now(TZ)
            time_ = datetime_tz.strftime("`%Y/%m/%d - %H:%M:%S`")
            final_tagged_msg = f"**🔔 You Have Been** [Tagged]({tagged_msg_link}) **in** {chat_name} **By** {user_} **At** {time_} with message:**\n\n{message_text}**"
            await client.send_message(
                LOG_CHAT,
                final_tagged_msg,
                disable_notification=False,
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        else:
            if not message:
                return
            if not message.from_user:
                return
            chat_name = message.chat.title
            chat_id = message.chat.id
            if chat_id < 0:
                chat_id = int(str(chat_id).replace("-100", ""))
            tagged_msg_link = "https://t.me/c/{}/{}".format(chat_id, message.id)
            message_text = ""
            if message.text:
                message_text = message.text
            else:
                message_text = message.caption
            user_ = f"@{message.from_user.username}" or message.from_user.mention
            TZ = pytz.timezone("Asia/Kolkata")
            datetime_tz = datetime.now(TZ)
            time_ = datetime_tz.strftime("`%Y/%m/%d - %H:%M:%S`")
            final_tagged_msg = f"This message has been sent to your saved message because you haven't saved a tag logger chat. \n\n**🔔 You Have Been** [Tagged]({tagged_msg_link}) **in** {chat_name} **By** {user_} **At** {time_} with message:**\n\n{message_text}**"
            await client.send_message(
                "me",
                final_tagged_msg,
                disable_notification=False,
                parse_mode=enums.ParseMode.MARKDOWN,
            )


modules_help["log_tag"] = {
    "log_tag_chat": "Set Tag Logger Chat. \nNOTE:Using this cmd in any group will set that group as tag logger",
    "log_tag_chat_rm": "Remove Tag Logger Chat. \nUse in group where tag logger is set",
    "log_tag_on": "Enable Tag Logger.",
    "log_tag_off": "Disable Tag Logger",
}
