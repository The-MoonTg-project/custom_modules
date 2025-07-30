import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

@Client.on_message(filters.command("del", prefix) & filters.me)
async def del_message(_, message: Message):
    if len(message.command) <= 2:
        await message.edit(
            "<b>❌ خطا:</b> <i>باید زمان (ثانیه) و متن پیام رو مشخص کنی</i>\n"
            "<b>مثال:</b> <code>.del 10 سلام دوستان!</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(5)
        await message.delete()
        return
    
    try:
        # گرفتن زمان از آرگومان دوم
        delete_time = int(message.command[1])
        
        # گرفتن متن از باقی آرگومان‌ها
        text = " ".join(message.command[2:])
        
        # بررسی محدودیت‌ها
        if delete_time <= 0:
            await message.edit(
                "<b>❌ خطا:</b> <i>زمان باید عدد مثبت باشه!</i>",
                parse_mode=enums.ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            return
            
        if delete_time > 86400:  # 24 ساعت
            await message.edit(
                "<b>❌ خطا:</b> <i>حداکثر زمان ۲۴ ساعت (۸۶۴۰۰ ثانیه) هست!</i>",
                parse_mode=enums.ParseMode.HTML,
            )
            await asyncio.sleep(5)
            await message.delete()
            return
        
        if not text.strip():
            await message.edit(
                "<b>❌ خطا:</b> <i>متن پیام نمی‌تونه خالی باشه!</i>",
                parse_mode=enums.ParseMode.HTML,
            )
            await asyncio.sleep(3)
            await message.delete()
            return
        
        # ویرایش پیام با متن جدید
        await message.edit(
            text,
            parse_mode=enums.ParseMode.HTML,
        )
        
        # منتظر موندن و حذف پیام
        await asyncio.sleep(delete_time)
        await message.delete()
        
    except ValueError:
        await message.edit(
            "<b>❌ خطا:</b> <i>زمان باید عدد صحیح باشه!</i>\n"
            "<b>مثال:</b> <code>.del 30 این پیام ۳۰ ثانیه دیگه حذف میشه</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.edit(
            f"<b>❌ خطای غیرمنتظره:</b> <code>{str(e)}</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(5)
        await message.delete()

modules_help["self_delete"] = {
    "del [time] [text]*": "ارسال پیام خودحذفشونده\n"
    "زمان: مدت زمان تا حذف (ثانیه)\n"
    "متن: محتوای پیام\n"
    "مثال: .del 60 این پیام یک دقیقه دیگه حذف میشه"
}