from pyrogram import Client, filters
from pyrogram.types import Message

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from aiohttp import ClientSession
from io import BytesIO

session = ClientSession()


class Post:
    def __init__(self, source: dict, session: ClientSession):
        self._json = source
        self.session = session

    @property
    async def image(self):
        return (
            self.file_url
            if self.file_url
            else self.large_file_url
            if self.large_file_url
            else self.source
            if self.source and "pximg" not in self.source
            else await self.pximg
            if self.source
            else None
        )

    @property
    async def pximg(self):
        async with self.session.get(self.source) as response:
            return BytesIO(await response.read())

    def __getattr__(self, item):
        return self._json.get(item)


async def random():
    async with session.get(
        url="https://danbooru.donmai.us/posts/random.json"
    ) as response:
        return Post(await response.json(encoding="utf-8"), session)


@Client.on_message(filters.command(["arnd", "arandom"], prefix) & filters.me)
async def anime_handler(client: Client, message: Message):
    try:
        await message.edit("<b>Searching art</b>")
        ra = await random()
        img = await ra.image
        await message.reply_photo(
            photo=img,
            caption=f'<b>{ra.tag_string_general if ra.tag_string_general else "Без названия"}</b>',
        )
        return await message.delete()
    except Exception as e:
        await message.edit(format_exc(e))


modules_help["anime"] = {
    "arnd": "Random anime art (May get caught 18+)",
}
