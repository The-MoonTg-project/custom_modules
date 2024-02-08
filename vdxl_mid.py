import requests, base64, os

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.config import vca_api_key
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, edit_or_reply


# Define the API endpoint
api_url = "https://visioncraft-rs24.koyeb.app"

@Client.on_message(filters.command("midxl", prefix) & filters.me)
async def vdxl_mid(c: Client, message: Message):
    try:
        chat_id = message.chat.id
        await message.edit_text("<code>Please Wait...</code>")

        if len(message.command) > 1:
         prompt = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
         prompt = message.reply_to_message.text
        else:
         await message.edit_text(
            f"<b>Usage: </b><code>{prefix}vdxl [prompt/reply to prompt]</code>"
        )
         return

        data = {
            "prompt": prompt,
            "model": "juggernaut-xl-V7",
            "negative_prompt": "",
            "token": vca_api_key,
            "width": 1024,
            "height": 768,
            "steps": 30,
            "cfg_scale": 8,
            "nsfw_filter": False,
            "watermark": False
        }
        
        # Send the request to generate images
          response = requests.post(f"{api_url}/premium/generate-xl", json=data)
        
        # Extract the image URLs from the response
        image_url = response.json()["images"][0]
        
        # Get the image data from the URL
        response = requests.get(image_url)
        # Save the image locally
        with open(f"generated_image.png", "wb") as f:
            f.write(response.content)

            await message.delete()
        #for i, image_url in enumerate(image_urls):
            await c.send_photo(chat_id, photo=f"generated_image.png", caption=f"<b>Prompt:</b><code>{prompt}</code>")
            os.remove(f"generated_image.png")

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")

modules_help["vdxl_mid"] = {
    "midxl [prompt/reply to prompt]*": "Text to Image with SDXL Midjourney model[Requires VisionCraft Premium]"
}
