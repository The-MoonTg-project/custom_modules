from pyrogram import Client, filters
from utils.misc import modules_help, prefix
import time
from sys import version_info
from pyrogram import __version__ as pyro_version

StartTime = time.time()

# Start Image Url @Tech_Shreyansh29
ALIVE_MEDIA = "https://i.ibb.co/B5MvLpkP/Uploaded-6910445402.jpg"

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

async def get_alive_text(client: Client, message):
    user = message.from_user
    uptime = get_readable_time((time.time() - StartTime))
    return (
        f"Welcome {user.mention(user.first_name)} To <a href='https://github.com/The-MoonTg-project/Moon-Userbot'>Moon-Userbot</a>\n\n"
        f" › User:   <code>{user.first_name}</code>\n"
        f" › Python:   <code>v{version_info.major}.{version_info.minor}.{version_info.micro}</code>\n"
        f" › Pyrogram:   <code>v{pyro_version}</code>\n"
        f" › Uptime:   <code>{uptime}</code>"
    )

@Client.on_message(filters.command("alive", prefix) & filters.me)
async def alive(client: Client, message):
    alive_text = await get_alive_text(client, message)
    
    if ALIVE_MEDIA and any(ALIVE_MEDIA.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=ALIVE_MEDIA,
            caption=alive_text
        )
    elif ALIVE_MEDIA and any(ALIVE_MEDIA.lower().endswith(ext) for ext in [".gif", ".mp4"]):
        await message.delete()
        await client.send_animation(
            chat_id=message.chat.id,
            animation=ALIVE_MEDIA,
            caption=alive_text
        )
    else:
        await message.edit(alive_text, disable_web_page_preview=True)

modules_help["alive"] = {
    "alive": "Check bot alive status"
}
