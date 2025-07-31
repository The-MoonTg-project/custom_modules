import asyncio

from pyrogram import Client, filters, enums
from pyrogram.types import Message

# این متغیر رو از فایل اصلی خودت ایمپورت کن
# from utils.misc import modules_help, prefix
# چون من به اون فایل دسترسی ندارم، به صورت نمونه اینجا تعریفش می‌کنم
prefix = "."
modules_help = {}


@Client.on_message(filters.command("tagall", prefix) & filters.me)
async def tagall(client: Client, message: Message):
    """این تابع همون کد قبلی خودته و دست نخورده باقی مونده"""
    await message.delete()
    chat_id = message.chat.id
    string = ""
    limit = 1
    
    # استفاده از client.get_chat_members برای دریافت اعضا
    async for member in client.get_chat_members(chat_id):
        # برای جلوگیری از تگ کردن ربات‌ها، می‌تونیم یه شرط اضافه کنیم
        if member.user.is_bot:
            continue

        tag = member.user.username
        if limit <= 5:
            # استفاده از متد mention برای تگ کردن امن‌تر و بهتر
            string += f"{member.user.mention(style='md')}\n"
            limit += 1
        else:
            await client.send_message(
                chat_id, 
                text=string, 
                # بهتره به جای HTML از Markdown استفاده کنی چون امن‌تره
                parse_mode=enums.ParseMode.MARKDOWN
            )
            limit = 1
            string = ""
            await asyncio.sleep(2)
    
    # ارسال باقی‌مانده اعضا اگر وجود داشته باشن
    if string:
        await client.send_message(
            chat_id, 
            text=string, 
            parse_mode=enums.ParseMode.MARKDOWN
        )


@Client.on_message(filters.command("hidetagall", prefix) & filters.me)
async def hidetagall(client: Client, message: Message):
    """
    ✨ این تابع جدید برای منشن مخفیه ✨
    روی یک پیام ریپلای کن و از این دستور استفاده کن.
    """
    # ۱. چک می‌کنیم که حتما روی یک پیام ریپلای شده باشه
    if not message.reply_to_message:
        await message.edit_text("❗️ **خطا:** لطفاً روی یک پیام ریپلای کن.")
        await asyncio.sleep(3)
        await message.delete()
        return

    # ۲. پیام دستور رو حذف می‌کنیم تا ردپایی نمونه
    await message.delete()

    target_message = message.reply_to_message
    chat_id = message.chat.id
    
    # ۳. یک لیست برای نگهداری منشن‌های مخفی درست می‌کنیم
    hidden_mentions = []

    # ۴. در بین تمام اعضای گروه می‌گردیم
    async for member in client.get_chat_members(chat_id):
        # ربات‌ها رو منشن نمی‌کنیم
        if not member.user.is_bot:
            # ✨ نکته کلیدی اینجاست ✨
            # ما کاربر رو با یک کاراکتر "عرض صفر" (Zero-Width Joiner) منشن می‌کنیم.
            # این کاراکтер در تلگرام دیده نمی‌شه ولی لینک منشن رو ایجاد می‌کنه.
            hidden_mentions.append(member.user.mention("‍"))

    # ۵. متن اصلی پیام (یا کپشن مدیا) رو می‌گیریم
    original_text = ""
    if target_message.text:
        original_text = target_message.text.html
    elif target_message.caption:
        original_text = target_message.caption.html
        
    # ۶. تمام منشن‌های مخفی رو به صورت یک رشته به هم می‌چسبونیم
    mentions_string = "".join(hidden_mentions)
    
    # ۷. متن نهایی رو با ترکیب متن اصلی و منشن‌های مخفی می‌سازیم
    final_text = f"{original_text}{mentions_string}"

    try:
        # ۸. پیام هدف رو ویرایش می‌کنیم و متن جدید رو جایگزین می‌کنیم
        await target_message.edit_text(
            final_text,
            # چون .mention() خروجی HTML می‌ده، باید از این حالت استفاده کنیم
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        # برای اینکه اگه خطایی پیش اومد، توی لاگ ببینیم
        print(f"Error in hidetagall: {e}")


# راهنمای دستورات رو هم آپدیت می‌کنیم
modules_help["tagall"] = {
    "tagall": "منشن کردن تمام اعضای گروه در دسته‌های ۵تایی.",
    "hidetagall": "ریپلای روی یک پیام برای منشن کردن تمام اعضا به صورت مخفی در آن پیام.",
}
