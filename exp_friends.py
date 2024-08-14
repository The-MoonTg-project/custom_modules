from pyrogram import Client, filters, enums
from pyrogram.types import Message
import os

from utils.misc import modules_help, prefix

@Client.on_message(filters.command("exp_friends", prefix) & filters.me)
async def fetch_info(client: Client, message: Message):
    # Edit the command message to show "Please wait"
    edited_message = await message.edit("Gathering information, please wait...")

    info = "Friends Information:\n\n"
    
    # Fetch and iterate over dialogs
    async for chat in client.get_dialogs():
        # Only include private chats
        if chat.chat.type == enums.ChatType.PRIVATE:
            # Get user details to exclude bots and fetch phone number
            user = await client.get_users(chat.chat.id)
            
            # Skip bots
            if user.is_bot:
                continue

            chat_info = f"ID: {chat.chat.id}\n"
            chat_info += f"Name: {chat.chat.first_name} {chat.chat.last_name}\n"
            chat_info += f"Username: @{chat.chat.username}\n"
            chat_info += f"Bio: {chat.chat.bio}\n" if chat.chat.bio else "Bio: Not available\n"
            
            # Add phone number if available
            phone_number = user.phone_number if user.phone_number else "Not available"
            chat_info += f"Phone Number: {phone_number}\n"
            
            # Check if user is a premium user
            premium_status = "Premium" if user.is_premium else "Not Premium"
            chat_info += f"Premium Status: {premium_status}\n"

            info += chat_info + "-"*20 + "\n"

    # Save the information to a text file
    file_path = "friends_info.txt"
    with open(file_path, "w") as file:
        file.write(info)

    # Upload the file to Telegram
    await client.send_document(
        chat_id=message.chat.id,  # Send to the same chat where the command was issued
        document=file_path,
        caption="Here is the information about your friends."
    )

    # Clean up: Remove the file after sending
    os.remove(file_path)

    # Delete the edited message once the result is ready
    await edited_message.delete()

# Adding module help instructions
modules_help["fetch_info"] = {
    "exp_friends": "Export friend's detail.",
}
