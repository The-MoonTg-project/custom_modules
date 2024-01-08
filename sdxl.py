import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from pyrogram import Client as Cl
from pyrogram import enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# Our Host URL should not be prepended with "https" nor should it have a trailing slash.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'


os.environ['STABILITY_KEY'] = 'your_api_key'

# Set up our connection to the API.
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True, 
    engine="stable-diffusion-xl-1024-v1-0", 
)


@Cl.on_message(filters.command("sdxl", prefix) & filters.me)
async def say(c: Cl, message: Message):
    try:
        chat_id = message.chat.id
        await message.edit_text("<code>Please Wait...</code>")

        if len(message.command) > 1:
         prompt = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
         prompt = message.reply_to_message.text
        else:
         await message.edit_text(
            f"<b>Usage: </b><code>{prefix}sdxl [prompt/reply to message]</code>"
        )
         return

        answers = stability_api.generate(
        prompt=prompt,
        seed=4253978046, 
        steps=50, 
        cfg_scale=8.0, 
        width=1024, 
        height=1024, 
        samples=1, 
        )
        
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = io.BytesIO(artifact.binary)
                    await message.delete()
                    await c.send_photo(chat_id, photo=img, caption=f"<b>Prompt:</b><code>{prompt}</code>")
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")

modules_help["sdxl"] = {
    "sdxl [prompt]*": "text to image sdxl",
}
