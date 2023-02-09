import asyncio
import datetime
import textwrap
from math import ceil

from pyrogram import Client, filters
from pyrogram.types import Message, Document

from utils.misc import modules_help, prefix
from utils.db import db
from utils.scripts import import_library

spotipy = import_library("spotipy")

client_id = "e0708753ab60499c89ce263de9b4f57a"
client_secret = "80c927166c664ee98a43a2c0e2981b4a"
scope = (
    "user-read-playback-state playlist-read-private playlist-read-collaborative"
    " app-remote-control user-modify-playback-state user-library-modify"
    " user-library-read"
)
sp_auth = spotipy.oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="https://fuccsoc.com/",
    scope=scope,
)


def auth_required(function):
    async def wrapped(client: Client, message: Message):
        if db.get("custom.spotify", "token") is None:
            await message.edit(
                f"<b>⚠️Для использования модуля необходима авторизация.\n"
                f"ℹ️Выполните <code>{prefix}spauth</code> для авторизации.</b>"
            )
        else:
            return await function(client, message)

    return wrapped


async def check_token():
    if db.get("custom.spotify", "token") is not None:
        if db.get("custom.spotify", "last_token_update") is None:
            db.set(
                "custom.spotify",
                "token",
                sp_auth.refresh_access_token(
                    db.get("custom.spotify", "token")["refresh_token"]
                ),
            )
            db.set(
                "custom.spotify",
                "last_token_update",
                datetime.datetime.now().isoformat(),
            )
        else:
            ttc = datetime.datetime.strptime(
                db.get("custom.spotify", "last_token_update"), "%Y-%m-%dT%H:%M:%S.%f"
            ) + datetime.timedelta(minutes=45)
            if ttc < datetime.datetime.now():
                db.set(
                    "custom.spotify",
                    "token",
                    sp_auth.refresh_access_token(
                        db.get("custom.spotify", "token")["refresh_token"]
                    ),
                )
                db.set(
                    "custom.spotify",
                    "last_token_update",
                    datetime.datetime.now().isoformat(),
                )


async def check_token_loop():
    while True:
        await check_token()
        await asyncio.sleep(600)


loop = asyncio.get_event_loop()
loop.create_task(check_token_loop())


@Client.on_message(filters.command("spauth", prefix) & filters.me)
async def auth(client: Client, message: Message):
    if not db.get("custom.spotify", "token") is None:
        await message.edit("⚠️Вы уже авторизованы")
    else:
        sp_auth.get_authorize_url()
        await message.edit(
            f'<a href="{sp_auth.get_authorize_url()}">ℹ️Перейдите по этой ссылке</a>,'
            " подтвердите доступ, затем скопируйте адрес редиректа и выполните"
            f" <code>{prefix}spcodeauth [адрес редедиректа]</code>"
        )


@Client.on_message(filters.command("spcodeauth", prefix) & filters.me)
async def codeauth(client: Client, message: Message):
    if db.get("custom.spotify", "token") is not None:
        await message.edit("⚠️Вы уже авторизованы")
    else:
        try:
            url = message.text.split(" ")[1]
            code = sp_auth.parse_auth_response_url(url)
            db.set(
                "custom.spotify", "token", sp_auth.get_access_token(code, True, False)
            )
            await message.edit(
                "<b>✅Авторизация успешна. Теперь вы можете использовать модуль\n"
                f"Список команд: <code>{prefix}help spotify</code></b>"
            )
        except Exception as e:
            await message.edit(
                "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
                f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
            )


@Client.on_message(filters.command("spunauth", prefix) & filters.me)
@auth_required
async def unauth(client: Client, message: Message):
    db.remove("custom.spotify", "token")
    db.remove("custom.spotify", "last_token_update")
    await message.edit("<b>✅Данные авторизации удалены успешно.</b>")


@Client.on_message(filters.command("spnow", prefix) & filters.me)
@auth_required
async def now(client: Client, message: Message):
    sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
    current_playback = sp.current_playback()
    success = True
    from_playlist = False
    try:
        track = current_playback["item"]["name"]
        artists = [
            '<a href="'
            + artist["external_urls"]["spotify"]
            + '">'
            + artist["name"]
            + "</a>"
            for artist in current_playback["item"]["artists"]
        ]
        artists_names = [
            artist["name"] for artist in current_playback["item"]["artists"]
        ]
        track_id = current_playback["item"]["id"]
        track_url = current_playback["item"]["external_urls"]["spotify"]
        device = (
            current_playback["device"]["name"]
            + " "
            + current_playback["device"]["type"].lower()
        )
        volume = str(current_playback["device"]["volume_percent"]) + "%"
        percentage = ceil(
            current_playback["progress_ms"]
            / current_playback["item"]["duration_ms"]
            * 100
        )
        bar_filled = ceil(percentage / 10)
        bar_empty = 10 - bar_filled
        bar = "".join("█" for _ in range(bar_filled))
        for _ in range(bar_empty):
            bar += "░"
        bar += (
            f" {str(int((current_playback['progress_ms'] / (1000 * 60)) % 60)).zfill(2)}:{str(int((current_playback['progress_ms'] / 1000) % 60)).zfill(2)} "
            f"/ {str(int((current_playback['item']['duration_ms'] / (1000 * 60)) % 60)).zfill(2)}:{str(int((current_playback['item']['duration_ms'] / 1000) % 60)).zfill(2)}"
        )
        bar += str(" (" + str(percentage) + "%)")
        try:
            from_playlist = True
            playlist_id = current_playback["context"]["uri"].split(":")[-1]
            playlist = sp.playlist(playlist_id)
            playlist_link = playlist["external_urls"]["spotify"]
            playlist_name = playlist["name"]
            playlist_owner = (
                '<a href = "'
                + playlist["owner"]["external_urls"]["spotify"]
                + '">'
                + playlist["owner"]["display_name"]
                + "</a>"
                + " <code>("
                + playlist["owner"]["id"]
                + ")</code>"
            )
        except:
            from_playlist = False
    except Exception as e:
        success = False

    if from_playlist and success:
        res = textwrap.dedent(
            f"""
                <b>🎶 Сейчас играет: <i>{", ".join(artists)} - <a href='{track_url}'>{track}</a> <a href="https://song.link/s/{track_id}">(другие платформы)</a></i>
                📱 Устройство: <code>{device}</code>
                🔊 Громкость: {volume}
                🎵 Плейлист: <a href="{playlist_link}">{playlist_name}</a> (<code>{playlist_id}</code>)
                🫂 Владелец плейлиста: {playlist_owner}
                
                <code>{bar}</code></b>
            """
        )
        err = False
        try:
            for r in (
                await client.get_inline_bot_results(
                    "vkm4bot", f"{', '.join(artists_names)} - {track}"
                )
            )["results"]:
                if r["type"] == "audio":
                    await client.send_cached_media(
                        message.chat.id,
                        Document._parse(client, r["document"], "audio")["file_id"],
                        res,
                        reply_to_message_id=(
                            message.reply_to_message.message_id
                            if message.reply_to_message is not None
                            else None
                        ),
                    )
                    await message.delete()
                    return
        except Exception as e:
            err = True
            res += (
                "\n<b>ℹ️Не удалось найти песню.\nОшибка:</b>"
                f" <code>{e.__class__.__name__}</code>"
            )
            await message.edit(res, disable_web_page_preview=True)
        if not err:
            res += "\n<b>ℹ️Не удалось найти песню.</b>"
            await message.edit(res, disable_web_page_preview=True)
    elif success:
        res = textwrap.dedent(
            f"""
                <b>🎶 Сейчас играет: <i>{", ".join(artists)} - <a href='{track_url}'>{track}</a> <a href="https://song.link/s/{track_id}">(другие платформы)</a></i>
                📱 Устройство: <code>{device}</code>
                🔊 Громкость: {volume}
                    
                <code>{bar}</code></b>
            """
        )

        try:
            for r in (
                await client.get_inline_bot_results(
                    "vkm4bot", f"{', '.join(artists_names)} - {track}"
                )
            )["results"]:
                if r["type"] == "audio":
                    await client.send_cached_media(
                        message.chat.id,
                        Document._parse(client, r["document"], "audio")["file_id"],
                        res,
                        reply_to_message_id=(
                            message.reply_to_message.message_id
                            if message.reply_to_message is not None
                            else None
                        ),
                    )
                    await message.delete()
                    return
        except:
            pass
        try:
            for r in (
                await client.get_inline_bot_results(
                    "spotifysavebot", f"{', '.join(artists_names)} - {track}"
                )
            )["results"]:
                if r["type"] == "audio":
                    await client.send_cached_media(
                        message.chat.id,
                        Document._parse(client, r["document"], "audio")["file_id"],
                        res,
                        reply_to_message_id=(
                            message.reply_to_message.message_id
                            if message.reply_to_message is not None
                            else None
                        ),
                    )
                    await message.delete()
                    return
        except:
            pass
        try:
            for r in (
                await client.get_inline_bot_results(
                    "lybot", f"{', '.join(artists_names)} - {track}"
                )
            )["results"]:
                if r["type"] == "audio":
                    await client.send_cached_media(
                        message.chat.id,
                        Document._parse(client, r["document"], "audio")["file_id"],
                        res,
                        reply_to_message_id=(
                            message.reply_to_message.message_id
                            if message.reply_to_message is not None
                            else None
                        ),
                    )
                    await message.delete()
                    return
        except:
            pass
        res += "\n<b>ℹ️Не удалось найти песню.</b>"
        await message.edit(res, disable_web_page_preview=True)
    else:
        await message.edit(
            "<b>⚠️Не удалось получить трек\n"
            "Проверьте, что Spotify включен и проигрывает трек</b>"
        )


@Client.on_message(filters.command("repeat", prefix) & filters.me)
@auth_required
async def repeat(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        sp.repeat("track")
        await message.edit("🔂Поставлено на репит успешно. Счастливого прослушивания!")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


@Client.on_message(filters.command("derepeat", prefix) & filters.me)
@auth_required
async def derepeat(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        sp.repeat("context")
        await message.edit("🎶Снято с репита успешно.")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


@Client.on_message(filters.command("next", prefix) & filters.me)
@auth_required
async def next(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        sp.next_track()
        await message.edit("⏭️Трек переключен успешно.")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


@Client.on_message(filters.command("pausetr", prefix) & filters.me)
@auth_required
async def pausetr(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        sp.pause_playback()
        await message.edit("⏸️Поставлено на паузу успешно.")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


@Client.on_message(filters.command("unpausetr", prefix) & filters.me)
@auth_required
async def unpausetr(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        sp.start_playback()
        await message.edit("▶️Снято с паузы успешно")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


@Client.on_message(filters.command("back", prefix) & filters.me)
@auth_required
async def back(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        sp.previous_track()
        await message.edit("◀️Вернул трек назад успешно.")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


@Client.on_message(filters.command("restr", prefix) & filters.me)
@auth_required
async def restr(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        sp.seek_track(0)
        await message.edit("🔁Трек перезапущен.")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


@Client.on_message(filters.command("liketr", prefix) & filters.me)
@auth_required
async def liketr(client: Client, message: Message):
    try:
        sp = spotipy.Spotify(auth=db.get("custom.spotify", "token")["access_token"])
        cupl = sp.current_playback()
        sp.current_user_saved_tracks_add([cupl["item"]["id"]])
        await message.edit("💚Лайкнуто!")
    except Exception as e:
        await message.edit(
            "<b>⚠️Произошла какая-то ошибка. Проверьте, что вы все делаете верно.\n"
            f"Ошибка:</b> <code>{e.__class__.__name__}</code>"
        )


modules_help["spotify"] = {
    "spauth": "First auth step",
    "spcodeauth": "Second auth step",
    "spunauth": "Remove auth data",
    "spnow": "Display now playing track",
    "repeat": "Set track on-repeat",
    "derepeat": "Set track out from repeat",
    "next": "Turn on next track",
    "back": "Turn on previous track",
    "restr": "Restart currently playing track from start",
    "liketr": "Like current playing track",
    "pausetr": "Pause current playing track",
    "unpausetr": "Play currently paused track",
}
