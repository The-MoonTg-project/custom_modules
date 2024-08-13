import asyncio
from utils.misc import modules_help, prefix
import requests

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






def fetch_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]  # Assuming the API returns a list of entries
    else:
        return None

def format_word_data(data):
    formatted_data = f"Word: {data['word']}\n"
    formatted_data += f"Phonetic: {data.get('phonetic', 'N/A')}\n"
    
    if 'phonetics' in data:
        formatted_data += "Phonetics:\n"
        for phonetic in data['phonetics']:
            formatted_data += f"  - {phonetic.get('text', 'N/A')}"
            if 'audio' in phonetic:
                formatted_data += f" (Audio: {phonetic['audio']})"
            formatted_data += "\n"

    formatted_data += f"Origin: {data.get('origin', 'N/A')}\n"
    
    if 'meanings' in data:
        formatted_data += "Meanings:\n"
        for meaning in data['meanings']:
            formatted_data += f"  Part of Speech: {meaning['partOfSpeech']}\n"
            for definition in meaning['definitions']:
                formatted_data += f"    - Definition: {definition['definition']}\n"
                if 'example' in definition:
                    formatted_data += f"      Example: {definition['example']}\n"
                if 'synonyms' in definition and definition['synonyms']:
                    formatted_data += f"      Synonyms: {', '.join(definition['synonyms'])}\n"
                if 'antonyms' in definition and definition['antonyms']:
                    formatted_data += f"      Antonyms: {', '.join(definition['antonyms'])}\n"
    
    return formatted_data
    
@Client.on_message(filters.command(["word", "worldid"], prefix) & filters.me)
async def define_word(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a word to define.")
        return
    
    word = message.command[1]
    word_data = fetch_word_data(word)
    
    if word_data:
        formatted_data = format_word_data(word_data)
        await message.reply(formatted_data)
    else:
        await message.reply("Sorry, I couldn't find the definition for that word.")

modules_help["define"] = {
    "define [query]*": "get definitions of a world",
    "word [query]*": "get world details",
}
