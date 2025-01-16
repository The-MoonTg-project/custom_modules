import random, os
from pyrogram import Client, filters
from utils.misc import modules_help, prefix

from pyrogram import enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Character sets for password generation
digits = "1234567890"
letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
special_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?/`~\"\\"

@Client.on_message(filters.command("password", prefix) & filters.me)
async def password(client, message):
    # Display inline keyboard for password type selection with emojis
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔢 Digit Only", callback_data="pw_type_digit")],
        [InlineKeyboardButton("🔤 Text Only", callback_data="pw_type_text")],
        [InlineKeyboardButton("🔑 Simple", callback_data="pw_type_simple")],
        [InlineKeyboardButton("🔒 Complex", callback_data="pw_type_complex")],
        [InlineKeyboardButton("🎲 Random", callback_data="pw_type_random")],
    ])
    await message.reply_text(
        text="Select the type of password you want to generate: 🔑",
        reply_markup=buttons
    )

# Callback query handler for password generation
@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    if query.data.startswith("pw_type_"):
        # Determine the password type
        pw_type = query.data.split("_")[2]

        # Randomly choose a password type if "random" is selected
        if pw_type == "random":
            pw_type = random.choice(["digit", "text", "simple", "complex"])

        # Default length (you can modify this to ask the user for length)
        limit = random.randint(8, 12)

        # Select character set based on type
        if pw_type == "digit":
            charset = digits
        elif pw_type == "text":
            charset = letters
        elif pw_type == "simple":
            charset = letters + digits
        elif pw_type == "complex":
            charset = letters + digits + special_chars
        else:
            await query.message.edit_text("❌ Invalid password type selected.")
            return

        # Generate 5 passwords
        passwords = []
        for _ in range(5):
            password = "".join(random.choices(charset, k=limit))
            passwords.append(password)

        # Join the passwords into a string with newlines
        passwords_str = '\n'.join(passwords)

        # Format response
        txt = f"""
<b>Password Type:</b> {pw_type.capitalize()} 🛠️
<b>Length:</b> {limit} 🔢
<b>Generated Passwords:</b>
<code>{passwords_str}</code>
"""

        # Add a Back button to go back to the previous password selection menu
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")],  # Back button
            [InlineKeyboardButton("🔄 Generate Again", callback_data=f"pw_type_{pw_type}")],
            [InlineKeyboardButton("ℹ️ omginfo", url="https://t.me/omg_info")]
        ])
        await query.message.edit_text(
            text=txt,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "back_to_main":
        # When the Back button is clicked, show the main menu again
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔢 Digit Only", callback_data="pw_type_digit")],
            [InlineKeyboardButton("🔤 Text Only", callback_data="pw_type_text")],
            [InlineKeyboardButton("🔑 Simple", callback_data="pw_type_simple")],
            [InlineKeyboardButton("🔒 Complex", callback_data="pw_type_complex")],
            [InlineKeyboardButton("🎲 Random", callback_data="pw_type_random")],
        ])
        await query.message.edit_text(
            text="Select the type of password you want to generate: 🔑",
            reply_markup=buttons
        )


modules_help["password"] = {
    "password": "generate password",
    
}
