import asyncio

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command("tagall", prefix) & filters.me)
async def tagall(client: Client, message: Message):
    await message.delete()
    chat_id = message.chat.id
    string = ""
    limit = 1
    icm = client.get_chat_members(chat_id)
    async for member in icm:
        tag = member.user.username
        if limit <= 5:
            string += f"@{tag}\n" if tag != None else f"{member.user.mention}\n"
            limit += 1
        else:
            await client.send_message(
                chat_id, text=string, parse_mode=enums.ParseMode.HTML
            )
            limit = 1
            string = ""
            await asyncio.sleep(2)


@Client.on_message(filters.command("hidetagall", prefix) & filters.me)
async def hidetagall(client: Client, message: Message):
    chat_id = message.chat.id
    
    # استخراج متن بعد از دستور
    command_text = message.text or message.caption or ""
    command_prefix = f"{prefix}hidetagall"
    remaining_text = command_text.replace(command_prefix, "", 1).strip()
    
    # دریافت تمام اعضای گروه
    members = []
    icm = client.get_chat_members(chat_id)
    async for member in icm:
        # فقط کاربران واقعی (نه بات‌ها و اکانت‌های حذف شده)
        if not member.user.is_deleted and not member.user.is_bot:
            members.append(member.user)
    
    # ایجاد رشته منشن مخفی
    invisible_char = "‍"  # Zero Width Joiner (U+200D)
    tag_parts = []
    
    # برای هر عضو یک کاراکتر مخفی با منشن
    for user in members:
        tag_parts.append(f"[{invisible_char}](tg://user?id={user.id})")
    
    # اتصال با فاصله بین کاراکترها
    tag_string = " ".join(tag_parts)
    
    # ترکیب با متن باقی‌مانده
    final_text = tag_string
    if remaining_text:
        final_text += f" {remaining_text}"
    
    # ادیت پیام اصلی
    try:
        if message.media:
            # اگر پیام دارای مدیا است، کپشن رو ادیت کن
            await message.edit_caption(final_text, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            # در غیر این صورت متن رو ادیت کن
            await message.edit_text(final_text, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        # اگر ادیت ممکن نبود، پیام رو حذف و جدید ارسال کن
        await message.delete()
        await client.send_message(chat_id, final_text, parse_mode=enums.ParseMode.MARKDOWN)


modules_help["tagall"] = {
    "tagall": "Tag all members",
    "hidetagall": "Invisibly tag all members using hidden characters",
}
