#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coder by @xtdevs

from utils.misc import prefix
from pyrogram import Client, filters
import requests

async def fake_card_json(limit=2):
    response = requests.get(f"https://fakerapi.it/api/v1/credit_cards?_quantity={limit}")
    if response.status_code == 200:
        data = response.json()
        try:
            credit_cards = data["data"]
            card_number = credit_cards[0]["number"]
            expired_card = credit_cards[0]["expiration"]
            owners = credit_cards[0]["owner"]
            return [card_number, expired_card, owners]
        except Exception as e:
            return f"Error: {e}"
    return "Error response"

@Client.on_message(filters.command("fakecc", prefix) & filters.me)
async def fakecard_(client: Client, message: Message):
    pro = await message.reply_text("`Processing.....`")
    _json = await fake_card_json()
    texted = ""
    texted += "<b>Card Number</b> : <code>{}</code>\n".format(_json[0])
    texted += "<b>Expired</b> : <code>{}</code>\n".format(_json[1])
    texted += "<b>Onwer</b> : <code>{}</code>\n".format(_json[2])
    await pro.edit_text(texted)
