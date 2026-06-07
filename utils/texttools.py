import os

from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.scripts import import_library

import_library("pyfiglet", "pyfiglet")
import pyfiglet

normiefont     = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "=", "(", ")"]
ancientfont    = ["ꍏ", "ꌃ", "ꉓ", "ꀸ", "ꍟ", "ꎇ", "ꁅ", "ꃅ", "ꀤ", "ꀭ", "ꀘ", "꒒", "ꎭ", "ꈤ", "ꂦ", "ᖘ", "ꆰ", "ꋪ", "ꌗ", "꓄", "ꀎ", "ᐯ", "ꅏ", "ꊼ", "ꌩ", "ꁴ"]
boxfont        = ["🄰", "🄱", "🄲", "🄳", "🄴", "🄵", "🄶", "🄷", "🄸", "🄹", "🄺", "🄻", "🄼", "🄽", "🄾", "🄿", "🅀", "🅁", "🅂", "🅃", "🅄", "🅅", "🅆", "🅇", "🅈", "🅉"]
bubblesfont    = ["Ⓐ", "Ⓑ", "Ⓒ", "Ⓓ", "Ⓔ", "Ⓕ", "Ⓖ", "Ⓗ", "Ⓘ", "Ⓙ", "Ⓚ", "Ⓛ", "Ⓜ", "Ⓝ", "Ⓞ", "Ⓟ", "Ⓠ", "Ⓡ", "Ⓢ", "Ⓣ", "Ⓤ", "Ⓥ", "Ⓦ", "Ⓧ", "Ⓨ", "Ⓩ"]
bubblessldfont = ["🄰", "🄱", "🄲", "🄳", "🄴", "🄵", "🄶", "🄷", "🄸", "🄹", "🄺", "🄻", "🄼", "🄽", "🄾", "🄿", "🅀", "🅁", "🅂", "🅃", "🅄", "🅅", "🅆", "🅇", "🅈", "🅉"]
doubletextfont = ["Ꭿ", "ℬ", "ℂ", "ⅅ", "ℰ", "ℱ", "Ꮆ", "ℋ", "ℐ", "Ꭻ", "Ꮶ", "ℒ", "ℳ", "ℕ", "Ꮎ", "ℙ", "ℚ", "ℛ", "Ѕ", "Ꮖ", "U", "Ꮙ", "Ꮗ", "X", "Ꮍ", "ℤ"]
downsidefont   = ["∀", "B", "Ↄ", "◖", "Ǝ", "Ⅎ", "⅁", "H", "I", "ſ", "K", "⅂", "W", "ᴎ", "O", "Ԁ", "Ό", "ᴚ", "S", "⊥", "∩", "ᴧ", "M", "X", "⅄", "Z"]
egyptianfont   = ["ค", "๒", "ς", "๔", "є", "Ŧ", "ﻮ", "ђ", "เ", "ן", "к", "l", "๓", "ภ", "๏", "ק", "ợ", "г", "ร", "t", "ย", "ש", "ฬ", "ץ", "א", "z"]
ghostfont      = ["𝕬", "𝕭", "𝕮", "𝕯", "𝕰", "𝕱", "𝕲", "𝕳", "𝕴", "𝕵", "𝕶", "𝕷", "𝕸", "𝕹", "𝕺", "𝕻", "𝕼", "𝕽", "𝕾", "𝕿", "𝖀", "𝖁", "𝖂", "𝖃", "𝖄", "𝖅"]
hwcapitalfont  = ["𝓐", "𝓑", "𝓒", "𝓓", "𝓔", "𝓕", "𝓖", "𝓗", "𝓘", "𝓙", "𝓚", "𝓛", "𝓜", "𝓝", "𝓞", "𝓟", "𝓠", "𝓡", "𝓢", "𝓣", "𝓤", "𝓥", "𝓦", "𝓧", "𝓨", "𝓩"]
hwslfont       = ["𝒶", "𝒷", "𝒸", "𝒹", "ℯ", "𝒻", "ℊ", "𝒽", "𝒾", "𝒿", "𝓀", "𝓁", "𝓂", "𝓃", "ℴ", "𝓅", "𝓆","𝓇", "𝓈", "𝓉", "𝓊", "𝓋", "𝓌", "𝓍", "𝓎", "𝓏"]
musicalfont    = ["♬", "ᖲ", "¢", "ᖱ", "៩", "⨏", "❡", "Ϧ", "ɨ", "ɉ", "ƙ", "ɭ", "៣", "⩎", "០", "ᖰ", "ᖳ", "Ʀ", "ន", "Ƭ", "⩏", "⩔", "Ɯ", "✗", "ƴ", "Ȥ"]
nightmarefont  = ["𝖆", "𝖇", "𝖈", "𝖉", "𝖊", "𝖋", "𝖌", "𝖍", "𝖎", "𝖏", "𝖐", "𝖑", "𝖒", "𝖓", "𝖔", "𝖕", "𝖖", "𝖗", "𝖘", "𝖙", "𝖚", "𝖛", "𝖜", "𝖝", "𝖞", "𝖟"]
smalldownside  = ["ɐ", "q", "ɔ", "p", "ə", "ɟ", "ɓ", "ɥ", "ı", "ɾ", "ʞ", "l", "ɯ", "u", "o", "p", "q", "ɹ", "s", "ʇ", "n", "ʌ", "ʍ", "x", "ʎ", "z"]
smasllcapsfont = ["ᴀ", "ʙ", "ᴄ", "ᴅ", "ᴇ", "ꜰ", "ɢ", "ʜ", "ɪ", "ᴊ", "ᴋ", "ʟ", "ᴍ", "ɴ", "ᴏ", "ᴘ", "ǫ", "ʀ", "s", "ᴛ", "ᴜ", "ᴠ", "ᴡ", "x", "ʏ", "ᴢ"]
smoothtextfont = ["ᗩ", "ᗷ", "ᑕ", "ᗞ", "ᗴ", "ᖴ", "Ꮐ", "ᕼ", "Ꮖ", "ᒍ", "Ꮶ", "Ꮮ", "ᗰ", "ᑎ", "ᝪ", "ᑭ", "ᑫ", "ᖇ", "ᔑ", "Ꭲ", "ᑌ", "ᐯ", "ᗯ", "᙭", "Ꭹ", "Ꮓ"]
subscriptfont  = ["ₐ", "ᵦ", "𝒸", "𝒹", "ₑ", "𝒻", "𝓰", "ₕ", "ᵢ", "ⱼ", "ₖ", "ₗ", "ₘ", "ₙ", "ₒ", "ₚ", "ᵩ", "ᵣ", "ₛ", "ₜ", "ᵤ", "ᵥ", "𝓌", "ₓ", "ᵧ", "𝓏", "₀", "₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉", "₊", "₋", "₌", "₍", "₎"]
superscriptfont= ["ᵃ", "ᵇ", "ᶜ", "ᵈ", "ᵉ", "ᶠ", "ᵍ", "ʰ", "ᶦ", "ʲ", "ᵏ", "ˡ", "ᵐ", "ⁿ", "ᵒ", "ᵖ", "ᵠ", "ʳ", "ˢ", "ᵗ", "ᵘ", "ᵛ", "ʷ", "ˣ", "ʸ", "ᶻ", "⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹", "⁺", "⁻", "⁼", "⁽", "⁾"]
tantextfont    = ["Ꭿ", "Ᏸ", "Ꮳ", "Ꮄ", "Ꮛ", "Ꮄ", "Ꮆ", "Ꮒ", "i", "Ꮰ", "Ꮶ", "l", "m", "Ꮑ", "Ꮻ", "Ꮅ", "Ꮔ", "ᖇ", "Ꭶ", "Ꮏ", "Ꮜ", "Ꮙ", "Ꮿ", "ﾒ", "Ꭹ", "Ꮓ"]
vaportextfont  = ["Ａ", "Ｂ", "Ｃ", "Ｄ", "Ｅ", "Ｆ", "Ｇ", "Ｈ", "Ｉ", "Ｊ", "Ｋ", "Ｌ", "Ｍ", "Ｎ", "Ｏ", "Ｐ", "Ｑ", "Ｒ", "Ｓ", "Ｔ", "Ｕ", "Ｖ", "Ｗ", "Ｘ", "Ｙ", "Ｚ"]
weebyfont      = ["卂", "乃", "匚", "刀", "乇", "下", "厶", "卄", "工", "丁", "长", "乚", "从", "𠘨", "口", "尸", "㔿", "尺", "丂", "丅", "凵", "リ", "山", "乂", "丫", "乙"]
zalfont        = ["A̎͠", "B̬͆", "C̾̑", "D̜ͪ", "E̢̖", "F̹ͅ", "G̨̪", "H̝̏", "I͈̲", "Jͧ", "͋K̢͐", "L͔͛", "Mͫͨ", "N͈͟", "Ȍ̲", "P͊͟", "Q̖̖", "R̶̚", "S͉̽", "Tͫ͊", "Ṳ̉", "V̘͆", "Wͣ͟", "Xͨ͠", "Y̶͢", "Z͎̭"]
BPFont         = ["α", "β", "ᴄ", "ძ", "ε", "ғ", "ց", "ɧ", "ι", "ᴊ", "к", "ℓ", "ɱ", "η", "σ", "ρ", "ϙ", "ɾ", "s", "τ", "υ", "ѵ", "ω", "χ", "γ", "ƶ"]

FONTS = {
    "ancient": dict(zip(normiefont, ancientfont)),
    "boxf": dict(zip(normiefont, boxfont)),
    "bubbles": dict(zip(normiefont, bubblesfont)),
    "bbubbles": dict(zip(normiefont, bubblessldfont)),
    "doublef": dict(zip(normiefont, doubletextfont)),
    "downf": dict(zip(normiefont, downsidefont)),
    "egyptf": dict(zip(normiefont, egyptianfont)),
    "ghostf": dict(zip(normiefont, ghostfont)),
    "handcf": dict(zip(normiefont, hwcapitalfont)),
    "handsf": dict(zip(normiefont, hwslfont)),
    "musical": dict(zip(normiefont, musicalfont)),
    "nmare": dict(zip(normiefont, nightmarefont)),
    "sdownf": dict(zip(normiefont, smalldownside)),
    "smallf": dict(zip(normiefont, smasllcapsfont)),
    "smothf": dict(zip(normiefont, smoothtextfont)),
    "subscript": dict(zip(normiefont, subscriptfont)),
    "superscript": dict(zip(normiefont, superscriptfont)),
    "tan": dict(zip(normiefont, tantextfont)),
    "tantext": dict(zip(normiefont, tantextfont)),
    "vapor": dict(zip(normiefont, vaportextfont)),
    "vaportext": dict(zip(normiefont, vaportextfont)),
    "weeb": dict(zip(normiefont, weebyfont)),
    "weeby": dict(zip(normiefont, weebyfont)),
    "weebyfont": dict(zip(normiefont, weebyfont)),
    "zal": dict(zip(normiefont, zalfont)),
    "zalfont": dict(zip(normiefont, zalfont)),
    "bp": dict(zip(normiefont, BPFont)),
}

@Client.on_message(filters.command(list(FONTS.keys()), prefix) & filters.me)
async def font_formatter(client: Client, message: Message):
    cmd = message.command[0]
    font_dict = FONTS.get(cmd)
    
    input_text = ""
    if len(message.command) > 1:
        input_text = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        input_text = message.reply_to_message.text
        
    if not input_text:
        await message.edit("`What am I supposed to change? Give text.`")
        return
        
    output = input_text
    for word, initial in font_dict.items():
        output = output.replace(word.lower(), initial)
        
    await message.edit(output)

@Client.on_message(filters.command("figlet", prefix) & filters.me)
async def figlet_art(client: Client, message: Message):
    op = await message.edit("`Figleting This Text xD`")
    
    CMD_FIG = {
        "slant": "slant",
        "3d": "3-d",
        "5line": "5lineoblique",
        "alpha": "alphabet",
        "banner": "banner3-D",
        "doh": "doh",
        "iso": "isometric1",
        "letter": "letters",
        "allig": "alligator",
        "dotm": "dotmatrix",
        "bubble": "bubble",
        "bulb": "bulbhead",
        "digi": "digital",
    }
    
    input_str = ""
    if len(message.command) > 1:
        input_str = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        input_str = message.reply_to_message.text
        
    if not input_str:
        await op.edit("`Please add some text to figlet`")
        return
        
    cmd_style = None
    text = input_str
    
    if "|" in input_str:
        parts = input_str.split("|", maxsplit=1)
        text = parts[0].strip()
        cmd_style = parts[1].strip()
        
    if cmd_style:
        try:
            font = CMD_FIG[cmd_style]
        except KeyError:
            await op.edit("`Invalid selected style.\nAvailable Styles :` [Click here](https://telegra.ph/Available-Figlet-Styles-08-04)", disable_web_page_preview=True)
            return
        result = pyfiglet.figlet_format(text, font=font)
    else:
        result = pyfiglet.figlet_format(text)
        
    await op.edit(f"`\n{result}\n`")

@Client.on_message(filters.command("ftext", prefix) & filters.me)
async def ftext(client: Client, message: Message):
    input_str = ""
    if len(message.command) > 1:
        input_str = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        input_str = message.reply_to_message.text
        
    if input_str:
        paytext = input_str
        pay = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
            paytext * 8,
            paytext * 8,
            paytext * 2,
            paytext * 2,
            paytext * 2,
            paytext * 6,
            paytext * 6,
            paytext * 2,
            paytext * 2,
            paytext * 2,
            paytext * 2,
            paytext * 2,
        )
    else:
        pay = "╭━━━╮\n┃╭━━╯\n┃╰━━╮\n┃╭━━╯\n┃┃\n╰╯\n"
    await message.edit(pay)

modules_help["texttools"] = {
    "ancient [text]": "Ancientify your text.",
    "boxf [text]": "Changes text to box font.",
    "bubbles [text]": "Changes text to bubble font.",
    "bbubbles [text]": "Changes text to black bubbles font.",
    "doublef [text]": "Changes text to double text font.",
    "downf [text]": "Changes text to uppercase downside font.",
    "egyptf [text]": "Changes text to Egyptian font.",
    "ghostf [text]": "Changes text to Ghost font.",
    "handcf [text]": "Changes text to uppercase handwritten font.",
    "handsf [text]": "Changes text to lowercase handwritten font.",
    "musical [text]": "Musify your text.",
    "nmare [text]": "Changes text to Nightmare font.",
    "sdownf [text]": "Changes text to lowercase upside down font.",
    "smallf [text]": "Changes text to Small Uppercase font.",
    "smothf [text]": "Smoothes your text.",
    "subscript [text]": "Changes text to subscript font.",
    "superscript [text]": "Changes text to superscript font.",
    "tan [text]": "Changes text to tantext font. Aliases: tantext",
    "vapor [text]": "Changes text to vaportext font. Aliases: vaportext",
    "weeb [text]": "Changes text to weeby font. Aliases: weeby, weebyfont",
    "zal [text]": "Changes text to zal font. Aliases: zalfont",
    "bp [text]": "Changes text to bp font.",
    "ftext [text]": "Try urself xD"
}
