import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import import_library

lottie = import_library("lottie")
from lottie.exporters import exporters
from lottie.importers import importers


@Client.on_message(filters.command("destroy", prefix) & filters.me)
async def destroy_sticker(client: Client, message: Message):
    """Destroy animated stickers by modifying their animation properties"""
    try:
        reply = message.reply_to_message
        if not reply or not reply.sticker or not reply.sticker.is_animated:
            return await message.edit(
                "**Please reply to an animated sticker!**",
                parse_mode=enums.ParseMode.MARKDOWN,
            )

        edit_msg = await message.edit(
            "**🔄 Destroying sticker...**", parse_mode=enums.ParseMode.MARKDOWN
        )

        # Download sticker
        tgs_path = await reply.download()
        if not tgs_path or not os.path.exists(tgs_path):
            return await edit_msg.edit(
                "**❌ Download failed!**", parse_mode=enums.ParseMode.MARKDOWN
            )

        # Conversion process
        json_path = "temp.json"
        output_path = "MoonUB.tgs"

        importer = importers.get_from_filename(tgs_path)
        if not importer:
            return await edit_msg.edit(
                "**❌ JSON conversion failed!**", parse_mode=enums.ParseMode.MARKDOWN
            )

        animation = importer.process(tgs_path)
        exporter = exporters.get_from_filename(json_path)
        exporter.process(animation, json_path)

        # Modify JSON data
        with open(json_path, "r+") as f:
            content = f.read()
            modified = (
                content.replace("[1]", "[2]")
                .replace("[2]", "[3]")
                .replace("[3]", "[4]")
                .replace("[4]", "[5]")
                .replace("[5]", "[6]")
            )
            f.seek(0)
            f.write(modified)
            f.truncate()

        importer = importers.get_from_filename(json_path)
        animation = importer.process(json_path)
        exporter = exporters.get_from_filename(output_path)
        exporter.process(animation, output_path)

        # Send result
        await message.reply_document(output_path, reply_to_message_id=reply.id)
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


modules_help["destroy"] = {"destroy [reply]": "Modify and destroy animated stickers"}
