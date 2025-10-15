# This scripts contains use cases for userbots
# This is used on my Moon-Userbot: https://github.com/The-MoonTg-project/Moon-Userbot
# YOu can check it out for uses example
import os

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library

genai = import_library("google.genai", "google-genai")

from utils.config import gemini_key

client = genai.Client(api_key=gemini_key)

generation_config_cook = {
    "temperature": 0.35,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

MODEL_NAME = "gemini-2.5-flash"

@Client.on_message(filters.command("getai", prefix) & filters.me)
async def getai(_, message: Message):
    local_file_path = None
    uploaded_file = None
    try:
        await message.edit_text("<code>Please Wait...</code>")
        
        try:
            if not message.reply_to_message or not message.reply_to_message.media:
                return await message.edit_text("<code>Please reply to an image...</code>")
            
            local_file_path = await message.reply_to_message.download()
        except Exception:
            return await message.edit_text("<code>Please reply to an image or media that can be downloaded.</code>")

        uploaded_file = client.files.upload(file=local_file_path)
        
        prompt = "Get details of given image, be as accurate as possible."

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, uploaded_file]
        )

        await message.edit_text(
            f"**Detail Of Image:** {response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")

    finally:
        if uploaded_file:
            client.files.delete(name=uploaded_file.name)
        if local_file_path and os.path.exists(local_file_path):
            os.remove(local_file_path)


@Client.on_message(filters.command("aicook", prefix) & filters.me)
async def aicook(_, message: Message):
    local_file_path = None
    uploaded_file = None
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.edit_text("<code>Please reply to an image...</code>")
    
    try:
        await message.edit_text("<code>Cooking...</code>")

        try:
            local_file_path = await message.reply_to_message.download()
        except Exception:
            return await message.edit_text("<code>Please reply to an image or media that can be downloaded.</code>")

        uploaded_file = client.files.upload(file=local_file_path)
        
        cook_contents = [
            "Accurately identify the baked good in the image and provide an appropriate and recipe consistent with your analysis. ",
            uploaded_file,
        ]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=cook_contents,
            config=generation_config_cook
        )

        await message.edit_text(
            f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    
    finally:
        if uploaded_file:
            client.files.delete(name=uploaded_file.name)
        if local_file_path and os.path.exists(local_file_path):
            os.remove(local_file_path)


@Client.on_message(filters.command("aiseller", prefix) & filters.me)
async def aiseller(_, message: Message):
    local_file_path = None
    uploaded_file = None
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.edit_text("<code>Please reply to a product image...</code>")

    try:
        await message.edit_text("<code>Generating...</code>")
        
        if len(message.command) > 1:
            taud = message.text.split(maxsplit=1)[1]
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}aiseller [target audience] [reply to product image]</code>"
            )

        try:
            local_file_path = await message.reply_to_message.download()
        except Exception:
            return await message.edit_text("<code>Please reply to an image or media that can be downloaded.</code>")

        uploaded_file = client.files.upload(file=local_file_path)
        
        sell_contents = [
            "Given an image of a product and its target audience, write an engaging marketing description",
            "Product Image: ",
            uploaded_file,
            "Target Audience: ",
            taud,
        ]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=sell_contents,
        )

        await message.edit_text(
            f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    
    finally:
        if uploaded_file:
            client.files.delete(name=uploaded_file.name)
        if local_file_path and os.path.exists(local_file_path):
            os.remove(local_file_path)

modules_help["aimage"] = {
    "getai [reply to image]*": "Get details of image with Ai",
    "aicook [reply to image]*": "Generate Cooking instrunctions of the given food image",
    "aiseller [target audience] [reply to product image]*": "Generate a promotional message for the given image product for the given target audience",
}
