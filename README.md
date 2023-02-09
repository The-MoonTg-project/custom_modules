<h2>Custom modules</h2>


<p>To add your module to the bot, create a pull request in the <a href='https://github.com/The-MoonTg-project/custom_modules/'>custom_modules</a> repository</p>
<p>Or send the module and its hash to me (<a href='https://t.me/Qbtaumai'>@Qbtaumai</a>)

```python3
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix


# if your module has packages from PyPi

# from utils.scripts import import_library
# example = import_library("example")

# import_library() will automatically install required library
# if it isn't installed


@Client.on_message(filters.command("example_edit", prefix) & filters.me)
async def example_edit(client: Client, message: Message):
    await message.edit("<code>This is an example module</code>")


@Client.on_message(filters.command("example_send", prefix) & filters.me)
async def example_send(client: Client, message: Message):
    await client.send_message(message.chat.id, "<b>This is an example module</b>")


# This adds instructions for your module
modules_help["example"] = {
    "example_send": "example send",
    "example_edit": "example edit",
}

# modules_help["example"] = { "example_send [text]": "example send" }
#                  |            |              |        |
#                  |            |              |        └─ command description
#           module_name         command_name   └─ optional command arguments
#        (only snake_case)   (only snake_case too)
```
