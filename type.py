import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# Define hieroglyphic frames for bird animation
BIRD_ANIMATION_FRAMES = [
    "𓅰",  # First bird hieroglyph
    "𓅬",  # Second bird hieroglyph
    "𓅭",  # Third bird hieroglyph
    "𓅮",  # Fourth bird hieroglyph
    "𓅯",  # Fifth bird hieroglyph
]

# Define fish animation frames
FISH_ANIMATION_FRAMES = [
    "𓆝",  # First fish symbol
    "𓆟",  # Second fish symbol
    "𓆞",  # Third fish symbol
    "𓆝",  # Fourth fish symbol
    "𓆟",  # Fifth fish symbol
]

# Define goat animation frames
GOAT_ANIMATION_FRAMES = [
    "𓃖",  # First goat symbol
    "𓃗",  # Second goat symbol
    "𓃘",  # Third goat symbol
    "𓃙",  # Fourth goat symbol
    "𓃚",  # Fifth goat symbol
    "𓃛",  # Sixth goat symbol
    "𓃜",  # Seventh goat symbol
]

# Typewriter command
@Client.on_message(filters.command(["type", "typewriter"], prefix) & filters.me)
async def type_cmd(_, message: Message):
    text = message.text.split(maxsplit=1)[1]
    typed = ""
    typing_symbol = "▒"

    for char in text:
        await message.edit(typed + typing_symbol)
        await asyncio.sleep(0.1)
        typed += char
        await message.edit(typed)
        await asyncio.sleep(0.1)

# Bird animation command
@Client.on_message(filters.command(["bird"], prefix) & filters.me)
async def bird_cmd(_, message: Message):
    try:
        for _ in range(5):  # Reduced loop to 5
            for frame in BIRD_ANIMATION_FRAMES:
                await message.edit(frame)  # Show each frame
                await asyncio.sleep(0.5)  # Control the speed of the animation
    except FloodWait as e:
        await asyncio.sleep(e.x)

# Fish animation command
@Client.on_message(filters.command(["fish"], prefix) & filters.me)
async def fish_cmd(_, message: Message):
    try:
        for _ in range(5):  # Reduced loop to 5
            for frame in FISH_ANIMATION_FRAMES:
                await message.edit(frame)  # Show each frame
                await asyncio.sleep(0.5)  # Control the speed of the animation
    except FloodWait as e:
        await asyncio.sleep(e.x)

# Goat animation command
@Client.on_message(filters.command(["goat"], prefix) & filters.me)
async def goat_cmd(_, message: Message):
    try:
        for _ in range(5):  # Reduced loop to 5
            for frame in GOAT_ANIMATION_FRAMES:
                await message.edit(frame)  # Show each frame
                await asyncio.sleep(0.5)  # Control the speed of the animation
    except FloodWait as e:
        await asyncio.sleep(e.x)


# Add command descriptions to modules_help
modules_help["type"] = {
    "type [text]": "Typing emulation. Don't use a lot of characters, you can receive a lot of floodwaits!",
    "bird": "Displays a bird hieroglyphic animation.",
    "fish": "Displays a fish animation using emojis.",
    "goat": "Displays a goat animation using emojis."
}
