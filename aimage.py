# This scripts contains use cases for userbots
# This is used on my Moon-Userbot: https://github.com/The-MoonTg-project/Moon-Userbot
# YOu can check it out for uses example
import os
from PIL import Image
import google.generativeai as genai

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from utils.config import gemini_key

genai.configure(api_key=gemini_key)

generation_config_cook = {
    "temperature": 0.35,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel("gemini-1.5-flash-latest")
model_cook = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", generation_config=generation_config_cook
)


@Client.on_message(filters.command("getai", prefix) & filters.me)
async def getai(_, message: Message):
    try:
        await message.edit_text("<code>Please Wait...</code>")
        try:
            base_img = await message.reply_to_message.download()
        except AttributeError:
            return await message.edit_text("<code>Please reply to an image...</code>")

        img = Image.open(base_img)
        prompt = "Get details of given image, be as accurate as possible."

        response = model.generate_content([prompt, img])

        await message.edit_text(
            f"**Detail Of Image:** {response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )
        os.remove(base_img)
        return
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("aicook", prefix) & filters.me)
async def aicook(_, message: Message):
    if message.reply_to_message:
        try:
            await message.edit_text("<code>Cooking...</code>")

            try:
                base_img = await message.reply_to_message.download()
            except AttributeError:
                return await message.edit_text("<code>Please reply to an image...</code>")

            img = Image.open(base_img)
            cook_img = [
                "Accurately identify the baked good in the image and provide an appropriate and recipe consistent with your analysis. ",
                img,
            ]

            response = model_cook.generate_content(cook_img)

            await message.edit_text(
                f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN
            )
            os.remove(base_img)
            return
        except Exception as e:
            await message.edit_text(str(e))
    return await message.edit_text("Kindly reply to an image!")


@Client.on_message(filters.command("aiseller", prefix) & filters.me)
async def aiseller(_, message: Message):
    if message.reply_to_message:
        try:
            await message.edit_text("<code>Generating...</code>")
            if len(message.command) > 1:
                taud = message.text.split(maxsplit=1)[1]
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}aiseller [target audience] [reply to product image]</code>"
                )

            try:
                base_img = await message.reply_to_message.download()
            except AttributeError:
                return await message.edit_text("<code>Please reply to an image...</code>")

            img = Image.open(base_img)
            sell_img = [
                "Given an image of a product and its target audience, write an engaging marketing description",
                "Product Image: ",
                img,
                "Target Audience: ",
                taud,
            ]

            response = model.generate_content(sell_img)

            await message.edit_text(
                f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN
            )
            os.remove(base_img)
            return
        except Exception:
            await message.edit_text(
                f"<b>Usage: </b><code>{prefix}aiseller [target audience] [reply to product image]</code>"
            )
    return await message.edit_text("Kindly reply to an image!")


modules_help["aimage"] = {
    "getai [reply to image]*": "Get details of image with Ai",
    "aicook [reply to image]*": "Generate Cooking instrunctions of the given food image",
    "aiseller [target audience] [reply to product image]*": "Generate a promotional message for the given image product for the given target audience",
}
