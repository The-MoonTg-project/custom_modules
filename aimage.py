import os
from PIL import Image
import google.generativeai as genai

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from utils.config import gemini_key

# Configure the Gemini API
genai.configure(api_key=gemini_key)

# Generation configurations
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


async def download_image(message: Message):
    """Downloads the image from the message and returns the file path."""
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.edit_text("Please reply to an image.")
        return None
    return await message.reply_to_message.download()


async def handle_ai_response(message: Message, prompt, img, model):
    """Handles the AI response generation and edits the message with the result."""
    try:
        await message.edit_text("<code>Processing...</code>")
        response = model.generate_content([prompt, img])
        if response.text:
            await message.edit_text(
                f"**Result:** {response.text}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.edit_text("AI couldn't generate a response. Try with a clearer image.")
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("getai", prefix) & filters.me)
async def getai(client, message: Message):
    base_img = None
    try:
        base_img = await download_image(message)
        if not base_img:
            return

        img = Image.open(base_img)
        prompt = "Get details of the given image, be as accurate as possible."
        await handle_ai_response(message, prompt, img, model)
    finally:
        if base_img:
            os.remove(base_img)


@Client.on_message(filters.command("aicook", prefix) & filters.me)
async def aicook(client, message: Message):
    base_img = None
    try:
        base_img = await download_image(message)
        if not base_img:
            return

        img = Image.open(base_img)
        prompt = "Identify the baked good in the image and provide a suitable recipe."
        await handle_ai_response(message, prompt, img, model_cook)
    finally:
        if base_img:
            os.remove(base_img)


@Client.on_message(filters.command("aiseller", prefix) & filters.me)
async def aiseller(client, message: Message):
    base_img = None
    try:
        if len(message.command) > 1:
            target_audience = message.text.split(maxsplit=1)[1]
        else:
            await message.edit_text(
                f"<b>Usage:</b>\n<code>{prefix}aiseller [target audience] [reply to product image]</code>"
            )
            return

        base_img = await download_image(message)
        if not base_img:
            return

        img = Image.open(base_img)
        prompt = f"Create a marketing description for this product targeting {target_audience}."
        await handle_ai_response(message, prompt, img, model)
    finally:
        if base_img:
            os.remove(base_img)


modules_help["aimage"] = {
    "getai [reply to image]*": "Get details of the image with AI.",
    "aicook [reply to image]*": "Generate a recipe based on the food image.",
    "aiseller [target audience] [reply to product image]*": "Generate a marketing description for the product and target audience.",
}
