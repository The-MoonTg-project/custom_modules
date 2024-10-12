import os
import PIL.Image
import google.generativeai as genai

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from utils.config import gemini_key

# Configure the Gemini API
genai.configure(api_key=gemini_key)

generation_config_cook = {
    "temperature": 0.35,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# Initialize AI models
model = genai.GenerativeModel("gemini-1.5-flash-latest")
model_cook = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", generation_config=generation_config_cook
)


@Client.on_message(filters.command("getai", prefix) & filters.me)
async def getai(_, message: Message):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.edit_text("Please reply to an image.")
        
        await message.edit_text("<code>Please Wait...</code>")
        base_img = await message.reply_to_message.download()
        
        img = PIL.Image.open(base_img)
        prompt = "Get details of the given image, be as accurate as possible."

        # Generate AI response
        response = model.generate_content([prompt, img])
        
        if response.text:
            await message.edit_text(
                f"**Detail Of Image:** {response.text}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit_text("AI couldn't generate a response. Please try again with a clearer image.")
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        os.remove(base_img)


@Client.on_message(filters.command("aicook", prefix) & filters.me)
async def aicook(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.edit_text("Please reply to an image.")
    
    try:
        await message.edit_text("<code>Cooking...</code>")
        base_img = await message.reply_to_message.download()

        img = PIL.Image.open(base_img)
        cook_img = [
            "Accurately identify the baked good in the image and provide an appropriate recipe consistent with your analysis.",
            img,
        ]

        # Generate AI response
        response = model_cook.generate_content(cook_img)

        if response.text:
            await message.edit_text(
                f"{response.text}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit_text("AI couldn't generate a recipe. Please try again with a clearer food image.")
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        os.remove(base_img)


@Client.on_message(filters.command("aiseller", prefix) & filters.me)
async def aiseller(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.edit_text("Please reply to an image.")

    try:
        if len(message.command) > 1:
            target_audience = message.text.split(maxsplit=1)[1]
        else:
            return await message.edit_text(
                f"<b>Usage:</b>\n"
                f"<code>{prefix}aiseller [target audience] [reply to product image]</code>"
            )

        await message.edit_text("<code>Generating...</code>")
        base_img = await message.reply_to_message.download()

        img = PIL.Image.open(base_img)
        sell_img = [
            "Given an image of a product and its target audience, write an engaging marketing description",
            "Product Image: ",
            img,
            "Target Audience: ",
            target_audience,
        ]

        # Generate AI response
        response = model.generate_content(sell_img)

        if response.text:
            await message.edit_text(
                f"{response.text}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit_text("AI couldn't generate a marketing description. Please try again with a clearer image.")
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        os.remove(base_img)


modules_help["aimage"] = {
    "getai [reply to image]*": "Get details of image with AI.",
    "aicook [reply to image]*": "Generate cooking instructions for the given food image.",
    "aiseller [target audience] [reply to product image]*": "Generate a promotional message for the product image and target audience.",
}
