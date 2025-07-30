import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

# فرض می‌کنم این‌ها در ساختار پروژه‌ی شما وجود دارند
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("lock", prefix) & filters.me)
async def lock_message(client: Client, message: Message):
    """
    Sends a message with content protection enabled.
    Can be used by replying to a message or by providing text directly.
    """
    # تشخیص اینکه آیا به پیامی ریپلای شده یا متنی همراه کامند ارسال شده
    text_to_send = ""
    
    # حالت اول: ریپلای روی یک پیام
    if message.reply_to_message:
        if message.reply_to_message.text:
            text_to_send = message.reply_to_message.text
    # حالت دوم: ارسال متن همراه با کامند
    else:
        # جدا کردن کامند از بقیه متن
        # message.text.split(None, 1) -> ['.lock', 'hello world']
        if len(message.command) > 1:
            text_to_send = message.text.split(None, 1)[1]

    # اگر هیچ متنی برای ارسال وجود نداشت
    if not text_to_send:
        try:
            await message.edit("✍️ **لطفاً یک متن بنویس یا به یک پیام ریپلای کن.**")
            await asyncio.sleep(3)
            await message.delete()
        except Exception:
            pass # اگر پیام قبلا پاک شده بود یا مشکلی پیش آمد
        return

    # ارسال پیام جدید با محتوای محافظت‌شده
    try:
        # اول پیام کامند خودت رو پاک کن
        await message.delete()
        
        # بعد پیام جدید رو با فلگ protect_content=True بفرست
        await client.send_message(
            chat_id=message.chat.id,
            text=text_to_send,
            protect_content=True  # این پارامتر جادو رو انجام می‌ده! ✨
        )
    except FloodWait as e:
        # برای مدیریت خطای اسپم تلگرام
        await asyncio.sleep(e.value)
    except Exception as e:
        # برای لاگ کردن خطاهای احتمالی دیگه
        print(f"Error in lock module: {e}")


# اضافه کردن راهنمای کامند به لیست راهنماها
modules_help["lock"] = {
    "lock [text]": "متن شما رو به صورت یک پیام غیرقابل فوروارد ارسال می‌کنه.",
    "lock (با ریپلای)": "متن پیام ریپلای شده رو به صورت غیرقابل فوروارد ارسال می‌کنه.",
}
