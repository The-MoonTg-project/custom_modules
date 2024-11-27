from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from urllib.parse import quote as urlquote
from html import escape
import cloudscraper
from utils.misc import modules_help, prefix


# CloudScraper instance
scraper = cloudscraper.create_scraper()

# Sticker search URL
combot_stickers_url = "https://combot.org/telegram/stickers?q="


def get_cbs_data(query, page, user_id):
    """Fetch sticker pack data and return text with pagination buttons."""
    text = scraper.get(f"{combot_stickers_url}{urlquote(query)}&page={page}").text
    soup = BeautifulSoup(text, "lxml")
    
    div = soup.find("div", class_="page__container")
    if not div:
        return "Failed to retrieve sticker packs. Please try again later.", None

    packs = div.find_all("a", class_="sticker-pack__btn")
    titles = div.find_all("div", "sticker-pack__title")
    
    has_prev_page = has_next_page = False
    highlighted_page = div.find("a", class_="pagination__link is-active")
    if highlighted_page and user_id:
        highlighted_page = highlighted_page.parent
        if highlighted_page:
            has_prev_page = highlighted_page.previous_sibling and highlighted_page.previous_sibling.previous_sibling is not None
            has_next_page = highlighted_page.next_sibling and highlighted_page.next_sibling.next_sibling is not None

    buttons = []
    if has_prev_page:
        buttons.append(InlineKeyboardButton("⟨", callback_data=f"cbs_{page - 1}_{user_id}"))
    if has_next_page:
        buttons.append(InlineKeyboardButton("⟩", callback_data=f"cbs_{page + 1}_{user_id}"))

    buttons = InlineKeyboardMarkup([buttons]) if buttons else None

    text = f"<b>Stickers for</b> <code>{escape(query)}</code>:\n<b>Page:</b> {page}"
    if packs and titles:
        for pack, title in zip(packs, titles):
            link = pack.get("href")
            text += f"\n• <a href='{link}'>{escape(title.get_text(strip=True))}</a>"
    elif page == 1:
        text = "No results found. Try a different search term."
    else:
        text += "\n\nNothing interesting here."

    return text, buttons




@Client.on_message(filters.command("sticker", prefix) & filters.me)
async def cb_sticker(client, message):
    """Handle sticker search command."""
    query = " ".join(message.command[1:])
    if not query:
        await message.reply_text("Please provide a term to search for sticker packs.")
        return
    if len(query) > 50:
        await message.reply_text("Search query must be under 50 characters.")
        return
    
    user_id = message.from_user.id if message.from_user else None
    text, buttons = get_cbs_data(query, 1, user_id)
    await message.reply_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)


@Client.on_callback_query(filters.regex(r"^cbs_"))
async def cbs_callback(client, callback_query):
    """Handle pagination callbacks."""
    _, page, user_id = callback_query.data.split("_", 2)
    if int(user_id) != callback_query.from_user.id:
        await callback_query.answer("Not for you.", show_alert=True, cache_time=60)
        return

    search_query = callback_query.message.text.split("\n", 1)[0].split(maxsplit=2)[2][:-1]
    text, buttons = get_cbs_data(search_query, int(page), callback_query.from_user.id)
    await callback_query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons)
    await callback_query.answer()



modules_help["sticker"] = {
    "sticker": "get search sticker",
}
    
