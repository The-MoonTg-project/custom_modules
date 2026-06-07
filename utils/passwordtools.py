import random
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%^&*()_+₹-=,./<>?';:|{}[]"

@Client.on_message(filters.command(["pass"], prefix) & filters.me)
async def rpass(client: Client, message: Message):
    if len(message.command) > 1:
        try:
            length = int(message.command[1])
        except ValueError:
            length = 10
    else:
        length = 10

    if length > 4000:
        await message.edit("`Password length is too long for a single message!`")
        return

    await message.edit("`Processing...`")
    
    password = "".join(random.choice(chars) for _ in range(length))
    
    await message.edit(f"Your random `{length}` character long password is:\n\n`{password}`")

modules_help["passwordtools"] = {
    "pass [length]": "Generates a random password of the specified length (default is 10)."
}
