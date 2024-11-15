import os
from PIL import Image
import google.generativeai as genai
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from utils.config import gemini_key

# Configure Generative AI
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

# Helper function to process image input
async def process_image(message, prompt, model_instance):
    try:
        await message.edit_text("<code>Processing...</code>")
        base_img = await message.reply_to_message.download()
        img = Image.open(base_img)

        response = model_instance.generate_content([prompt, img])
        if not response or not response.text.strip():
            return await message.edit_text("No result returned. Please try again!")

        await message.edit_text(
            f"{response.text.strip()}", parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        if os.path.exists(base_img):
            os.remove(base_img)

# Commands
@Client.on_message(filters.command("getai", prefix) & filters.me)
async def getai(_, message: Message):
    if not (reply := message.reply_to_message) or not reply.photo:
        return await message.edit_text("Please reply to an image!")
    await process_image(
        message,
        "Get details of the given image, be as accurate as possible.",
        model,
    )

@Client.on_message(filters.command("aicook", prefix) & filters.me)
async def aicook(_, message: Message):
    if not (reply := message.reply_to_message) or not reply.photo:
        return await message.edit_text("Please reply to a food image!")
    await process_image(
        message,
        "Identify the food item in the image and provide a detailed recipe.",
        model_cook,
    )

@Client.on_message(filters.command("aiseller", prefix) & filters.me)
async def aiseller(_, message: Message):
    if not (reply := message.reply_to_message) or not reply.photo:
        return await message.edit_text("Please reply to a product image!")
    args = message.text.split(maxsplit=1)[1:]  # Extract target audience
    if not args:
        return await message.edit_text(
            f"<b>Usage:</b> <code>{prefix}aiseller [target audience]</code>"
        )

    try:
        await message.edit_text("<code>Generating marketing description...</code>")
        base_img = await reply.download()
        img = Image.open(base_img)

        prompt = f"Write an engaging marketing description for this product targeting '{args[0]}'."
        response = model.generate_content([prompt, img])

        if not response or not response.text.strip():
            return await message.edit_text("No result returned. Please try again!")

        await message.edit_text(
            f"{response.text.strip()}", parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        if os.path.exists(base_img):
            os.remove(base_img)

# Help documentation
modules_help["aimage"] = {
    "getai [reply to image]*": "Get details of an image using AI.",
    "aicook [reply to image]*": "Generate a recipe based on a food image.",
    "aiseller [target audience] [reply to product image]*": "Generate a marketing description for the given product image and target audience.",
}
