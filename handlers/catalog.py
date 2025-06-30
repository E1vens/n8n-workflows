from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_top_products_by_category, get_distinct_categories
from handlers.language import get_user_language, get_translated_text
from math import ceil
from urllib.parse import quote
from hashlib import sha1

PAGE_SIZE = 5
category_map = {}

# Переводы названий категорий
CATEGORY_TRANSLATIONS = {
    "Виски": {"ru": "Виски", "en": "Whisky", "es": "Whisky"},
    "Водка": {"ru": "Водка", "en": "Vodka", "es": "Vodka"},
    "Джин": {"ru": "Джин", "en": "Gin", "es": "Ginebra"},
    "Вино": {"ru": "Вино", "en": "Wine", "es": "Vino"},
    "Крепкое вино": {"ru": "Крепкое вино", "en": "Fortified wine", "es": "Vino fortificado"},
    "Шампанское и игристое": {"ru": "Шампанское и игристое", "en": "Sparkling wine", "es": "Vino espumoso"},
    "Коньяк и Арманьяк": {"ru": "Коньяк и Арманьяк", "en": "Cognac & Armagnac", "es": "Coñac y Armagnac"},
    "Кальвадос": {"ru": "Кальвадос", "en": "Calvados", "es": "Calvados"},
    "Другие": {"ru": "Другие", "en": "Other", "es": "Otros"},
}

def translate_category(cat, lang):
    return CATEGORY_TRANSLATIONS.get(cat, {}).get(lang, cat)

# 👉 Категории (при нажатии на кнопку "Каталог")
async def handle_catalog_overview(chat_id: int, send_message):
    print("✅ handle_catalog_overview вызван")

    lang = get_user_language(chat_id)
    categories = await run_in_threadpool(get_distinct_categories)
    print("📦 Категории из Supabase:", categories)

    if not categories:
        return await send_message(chat_id, get_translated_text(chat_id, "no_categories"))

    keyboard = []
    for cat in categories:
        cat_id = sha1(cat.encode()).hexdigest()[:8]
        category_map[cat_id] = cat
        display_name = translate_category(cat, lang)
        keyboard.append([InlineKeyboardButton(text=display_name, callback_data=f"cat|{cat_id}|1")])

    markup = InlineKeyboardMarkup(keyboard).to_dict()
    return await send_message(chat_id, get_translated_text(chat_id, "select_category"), reply_markup=markup)

# 👉 Товары по категории
async def handle_category_selection(chat_id: int, cat_id: str, send_message, page: int = 1):
    category = category_map.get(cat_id)
    if not category:
        return await send_message(chat_id, get_translated_text(chat_id, "unknown_category"))

    all_products = await run_in_threadpool(get_top_products_by_category, category, limit=1000)
    if not all_products:
        return await send_message(chat_id, get_translated_text(chat_id, "empty_category").replace("{category}", category))

    total_pages = ceil(len(all_products) / PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    products = all_products[start:end]

    for product in products:
        photo = (
            product.get("image_url")
            or product.get("metadata", {}).get("image")
            or product.get("metadata->>image")
        )

        text = (
            f"*{product.get('title', 'Без названия')}*\n"
            f"{get_translated_text(chat_id, 'price')}: {product.get('price', '?')}₽\n"
            f"{get_translated_text(chat_id, 'volume')}: {product.get('volume', '?')} • "
            f"{get_translated_text(chat_id, 'strength')}: {product.get('strength', '?')}\n"
            f"[🔗 {get_translated_text(chat_id, 'view_product')}]({product.get('product_url', '#')})"
        )

        await send_message(chat_id, text, photo=photo)

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(get_translated_text(chat_id, "back"), callback_data=f"cat|{cat_id}|{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(get_translated_text(chat_id, "next"), callback_data=f"cat|{cat_id}|{page + 1}"))

    if nav_buttons:
        markup = InlineKeyboardMarkup([nav_buttons]).to_dict()
        await send_message(
            chat_id,
            get_translated_text(chat_id, "page_info").replace("{page}", str(page)).replace("{total}", str(total_pages)),
            reply_markup=markup
        )
    else:
        await send_message(
            chat_id,
            get_translated_text(chat_id, "page_info").replace("{page}", str(page)).replace("{total}", str(total_pages))
        )
