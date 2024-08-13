import asyncio
from utils.misc import modules_help, prefix


from pyrogram import Client, enums,filters
from pyrogram.types import Message
import json

import aiohttp

class AioHttp:
    @staticmethod
    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()



@Client.on_message(filters.command("define", prefix) & filters.me)
async def define( Client,message: Message):
    Message = message.command

    input_string = ""
    if len(Message) > 1:
        input_string = " ".join(Message[1:])
    elif message.reply_to_message and len(Message) == 1:
        input_string = message.reply_to_message.text
    elif not message.reply_to_message and len(Message) == 1:
        await message.reply("`Can't pass to the void.`")
        return

    def combine(s_word, name):
        w_word = f"**__{name.title()}__**\n"
        for i in s_word:
            if "definition" in i:
                if "example" in i:
                    w_word += (
                            "\n**Definition**\n<pre>"
                            + i["definition"]
                            + "</pre>\n<b>Example</b>\n<pre>"
                            + i["example"]
                            + "</pre>"
                    )
                else:
                    w_word += (
                            "\n**Definition**\n" + "<pre>" + i["definition"] + "</pre>"
                    )
        w_word += "\n\n"
        return w_word

    def out_print(word1):
        out = ""
        if "meaning" in list(word1):
            meaning = word1["meaning"]
            if "noun" in list(meaning):
                noun = meaning["noun"]
                out += combine(noun, "noun")
            if "verb" in list(meaning):
                verb = meaning["verb"]
                out += combine(verb, "verb")
            if "preposition" in list(meaning):
                preposition = meaning["preposition"]
                out += combine(preposition, "preposition")
            if "adverb" in list(meaning):
                adverb = meaning["adverb"]
                out += combine(adverb, "adverb")
            if "adjective" in list(meaning):
                adjec = meaning["adjective"]
                out += combine(adjec, "adjective")
            if "abbreviation" in list(meaning):
                abbr = meaning["abbreviation"]
                out += combine(abbr, "abbreviation")
            if "exclamation" in list(meaning):
                exclamation = meaning["exclamation"]
                out += combine(exclamation, "exclamation")
            if "transitive verb" in list(meaning):
                transitive_verb = meaning["transitive verb"]
                out += combine(transitive_verb, "transitive verb")
            if "determiner" in list(meaning):
                determiner = meaning["determiner"]
                out += combine(determiner, "determiner")
                # print(determiner)
            if "crossReference" in list(meaning):
                crosref = meaning["crossReference"]
                out += combine(crosref, "crossReference")
        if "title" in list(word1):
            out += (
                    "**__Error Note__**\n\n▪️`"
                    + word1["title"]
                    + "\n\n▪️"
                    + word1["message"]
                    + "\n\n▪️<i>"
                    + word1["resolution"]
                    + "</i>`"
            )
        return out

    if not input_string:
        await message.reply("`Plz enter word to search‼️`")
    else:
        word = input_string
        r_dec = await AioHttp().get_json(
            f"https://api.dictionaryapi.dev/api/v1/entries/en/{word}"
        )

        v_word = input_string
        if isinstance(r_dec, list):
            r_dec = r_dec[0]
            v_word = r_dec["word"]
        last_output = out_print(r_dec)
        if last_output:
            await message.reply(
                "`Search result for   `" + f" {v_word}\n\n" + last_output
            )
        else:
            await message.reply("`No result found from the database.`")


modules_help["define"] = {
    "define *": "Get details of words ",

