import base64, os

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, import_library

clarifai = import_library("clarifai")

from clarifai.client.model import Model

@Client.on_message(filters.command("cdxl", prefix) & filters.me)
async def cdxl(c: Client, message: Message):
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

        inference_params = dict(width= 1024, height= 1024, steps=50, cfg_scale = 9.0)

        model_prediction = Model("https://clarifai.com/stability-ai/stable-diffusion-2/models/stable-diffusion-xl").predict_by_bytes(prompt.encode(), input_type="text", inference_params=inference_params)

        output_base64 = model_prediction.outputs[0].data.image.base64
        
        
        
        with open('sdxl_out.png', 'wb') as f:
            f.write(output_base64)

            await message.delete()
            await c.send_photo(chat_id, photo=f"sdxl_out.png", caption=f"<b>Prompt:</b><code>{prompt}</code>")
            os.remove(f"sdxl_out.png")

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")

modules_help["cdxl"] = {
    "cdxl [prompt/reply to prompt]*": "Text to Image with SDXL model",
}
