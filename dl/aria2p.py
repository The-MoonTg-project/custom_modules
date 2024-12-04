# Thanks To SpEcHiDe sir for helping
# Thanks to me for modifying the wrong codes and make them workable
# feel free to use this in any pyrogram library userbot plugin you'll face no errors
import os
import asyncio
import io
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, requirements_list, prefix
from utils.scripts import import_library

logging = import_library("logging")
aria2p = import_library("aria2p")
import aria2p
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

cmd = "aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port 6800  --max-connection-per-server=10 --rpc-max-request-size=1024M --seed-time=0.01 --min-split-size=10M --follow-torrent=mem --split=10 --daemon=true --allow-overwrite=true"
EDIT_SLEEP_TIME_OUT = 6
aria2_is_running = os.system(cmd)
aria2 = aria2p.API(aria2p.Client(host="http://localhost", port=6800, secret=""))


@Client.on_message(filters.command("addmag", prefix) & filters.me)
async def magnet_download(client: Client, message: Message):
    var = message.text
    var = var[8:]
    magnet_uri = var
    magnet_uri = magnet_uri.replace("`", "")
    logger.info(magnet_uri)
    try:  # Add Magnet URI Into Queue
        download = aria2.add_magnet(magnet_uri)
    except Exception as e:
        logger.info(str(e))
        await message.edit_text("Error :\n{}".format(str(e)))
        return
    gid = download.gid
    await progress_status(gid=gid, message=message, previous=None)
    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
    new_gid = await check_metadata(gid)
    await progress_status(gid=new_gid, message=message, previous=None)


@Client.on_message(filters.command("addtor", prefix) & filters.me)
async def torrent_download(client: Client, message: Message):
    var = message.text[8:]
    torrent_file_path = var
    torrent_file_path = torrent_file_path.replace("`", "")
    logger.info(torrent_file_path)

    try:  # Add Torrent Into Queue
        download = aria2.add_torrent(
            torrent_file_path, uris=None, options=None, position=None
        )
    except Exception as e:
        await message.edit_text("Error :\n`{}`".format(str(e)))
        return
    gid = download.gid
    await progress_status(gid=gid, message=message, previous=None)


@Client.on_message(filters.command("ariaRM", prefix) & filters.me)
async def remove_all(client: Client, message: Message):
    try:
        removed = aria2.remove_all(force=True)
        aria2.purge_all()
    except:
        pass
    if removed == False:  # If API returns False Try to Remove Through System Call.
        os.system("aria2p remove-all")
    await message.edit_text("`Removed All Downloads.`")


@Client.on_message(filters.command("ariaP", prefix) & filters.me)
async def pause_all(client: Client, message: Message):
    # Pause ALL Currently Running Downloads.
    paused = aria2.pause_all(force=True)
    await message.edit_text("Output: " + str(paused))


@Client.on_message(filters.command("ariaR", prefix) & filters.me)
async def resume_all(client: Client, message: Message):
    resumed = aria2.resume_all()
    await message.edit_text("Output: " + str(resumed))


@Client.on_message(filters.command("ariastatus", prefix) & filters.me)
async def show_all(client: Client, message: Message):
    output = "output.txt"
    downloads = aria2.get_downloads()
    msg = ""
    for download in downloads:
        msg = (
            msg
            + "File: `"
            + str(download.name)
            + "`\nSpeed: "
            + str(download.download_speed_string())
            + "\nProgress: "
            + str(download.progress_string())
            + "\nTotal Size: "
            + str(download.total_length_string())
            + "\nStatus: "
            + str(download.status)
            + "\nETA:  "
            + str(download.eta_string())
            + "\n\n"
        )
    if len(msg) <= 4096:
        await message.edit_text("`Current Downloads: `\n" + msg)
    else:
        await message.edit_text("`Output is huge.Sending as file.. `")
        with open(output, "w") as f:
            f.write(msg)
        await asyncio.sleep(2)
        await message.delete()
        await client.send_document(
            chat_id=message.chat_id,
            document=output,
            caption="`Output is huge. Sending as a file...`",
        )


async def check_metadata(gid):
    file = aria2.get_download(gid)
    new_gid = file.followed_by_ids[0]
    logger.info("Changing GID " + gid + " to " + new_gid)
    return new_gid


async def progress_status(gid, message, previous):
    try:
        file = aria2.get_download(gid)
        if not file.is_complete:
            if not file.error_message:
                msg = (
                    "Downloading File: `"
                    + str(file.name)
                    + "`\nSpeed: "
                    + str(file.download_speed_string())
                    + "\nProgress: "
                    + str(file.progress_string())
                    + "\nTotal Size: "
                    + str(file.total_length_string())
                    + "\nStatus: "
                    + str(file.status)
                    + "\nETA:  "
                    + str(file.eta_string())
                    + "\n\n"
                )
                if previous != msg:
                    await message.edit_text(msg)
                    previous = msg
            else:
                logger.info(str(file.error_message))
                await message.edit_text("Error : `{}`".format(str(file.error_message)))
                retur
            await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
            await progress_status(gid, message, previous)
        else:
            await message.edit_text(
                "File Downloaded Successfully: `{}`".format(file.name)
            )
            return
    except Exception as e:
        if " not found" in str(e) or "'file'" in str(e):
            await message.edit_text("Download Canceled :\n`{}`".format(file.name))
            return
        elif " depth exceeded" in str(e):
            file.remove(force=True)
            await message.edit_text(
                "Download Auto Canceled :\n`{}`\nYour Torrent/Link is Dead.".format(
                    file.name
                )
            )
        else:
            logger.info(str(e))
            await message.edit_text("Error :\n`{}`".format(str(e)))
            return


modules_help["aria2"] = {
    "Special Thanks": "SpeechiDe sir",
    "addmag [magnet url]*": "Magnet link",
    "addtor [torrent file_path]*": "Torrent file from local",
    "ariaRM": "Remove All Downloads",
    "ariaP": "Pause All Downloads",
    "ariaR": "Resume All Downloads",
    "ariastatus": "Show Downloads",
}
