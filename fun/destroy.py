import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import import_library

lottie = import_library("lottie")


@Client.on_message(filters.command("destroy", prefix) & filters.me)
async def destroy_sticker(client: Client, message: Message):
    """Destroy animated stickers by modifying their animation properties"""
    try:
        reply = message.reply_to_message
        if not reply or not reply.sticker or not reply.sticker.is_animated:
            return await message.edit(
                "**Please reply to an animated sticker!**",
                parse_mode=enums.ParseMode.MARKDOWN
            )

        edit_msg = await message.edit("**🔄 Destroying sticker...**", parse_mode=enums.ParseMode.MARKDOWN)

        # Download sticker
        tgs_path = await client.download_media(reply)
        if not tgs_path or not os.path.exists(tgs_path):
            return await edit_msg.edit("**❌ Download failed!**", parse_mode=enums.ParseMode.MARKDOWN)

        # Conversion process
        json_path = "temp.json"
        output_path = "MoonUB.tgs"

        os.system(f"lottie_convert.py {tgs_path} {json_path}")
        if not os.path.exists(json_path):
            return await edit_msg.edit("**❌ JSON conversion failed!**", parse_mode=enums.ParseMode.MARKDOWN)

        # Modify JSON data
        with open(json_path, "r+") as f:
            content = f.read()
            modified = content.replace("[1]", "[2]") \
                              .replace("[2]", "[3]") \
                              .replace("[3]", "[4]") \
                              .replace("[4]", "[5]") \
                              .replace("[5]", "[6]")
            f.seek(0)
            f.write(modified)
            f.truncate()

        # Convert back to TGS
        os.system(f"lottie_convert.py {json_path} {output_path}")
        if not os.path.exists(output_path):
            return await edit_msg.edit("**❌ Final conversion failed!**", parse_mode=enums.ParseMode.MARKDOWN)

        # Send result
        await message.reply_document(
            output_path,
            reply_to_message_id=reply.id
        )
        await edit_msg.delete()

    except Exception as e:
        await message.edit(f"**❌ Error:** `{e}`", parse_mode=enums.ParseMode.MARKDOWN)
    finally:
        # Cleanup temporary files
        for file_path in [tgs_path, json_path, output_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as clean_error:
                    print(f"Cleanup error: {clean_error}")


modules_help["destroy"] = {
    "destroy [reply]": "Modify and destroy animated stickers"
}
