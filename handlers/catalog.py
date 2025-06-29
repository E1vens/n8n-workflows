from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_top_products_by_category, get_distinct_categories
from math import ceil
from urllib.parse import quote

PAGE_SIZE = 5

# 👉 Категории (при нажатии на кнопку "Каталог")
async def handle_catalog_overview(chat_id: int, send_message):
    print("✅ handle_catalog_overview вызван")

    categories = await run_in_threadpool(get_distinct_categories)
    print("📦 Категории из Supabase:", categories)

    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    keyboard = []

    for cat in categories:
        encoded = quote(cat)
        if len(f"category|{encoded}|1") > 64:
            encoded = quote(cat[:16])  # безопасная обрезка
        keyboard.append([
            InlineKeyboardButton(text=cat, callback_data=f"category|{encoded}|1")
        ])

    markup = InlineKeyboardMarkup(keyboard).to_dict()
    print("🎛 Inline клавиатура:", markup)

    return await send_message(
        chat_id,
        "📦 Выберите категорию товара:",
        reply_markup=markup
    )

# 👉 Товары по категории
async def handle_category_selection(chat_id: int, category: str, send_message, page: int = 1):
    all_products = await run_in_threadpool(get_top_products_by_category, category, limit=1000)
    if not all_products:
        return await send_message(chat_id, f"⚠️ В категории *{category}* ничего не найдено.")

    total_pages = ceil(len(all_products) / PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    products = all_products[start:end]

    for product in products:
        text = (
            f"*{product.get('title', 'Без названия')}*\n"
            f"Цена: {product.get('price', '?')}₽\n"
            f"Объём: {product.get('volume', '?')} • "
            f"Крепость: {product.get('strength', '?')}\n"
            f"[🔗 Открыть товар]({product.get('product_url', '#')})"
        )
        await send_message(chat_id, text, photo=product.get("image_url"))

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"category|{quote(category)}|{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"category|{quote(category)}|{page + 1}"))

    if nav_buttons:
        markup = InlineKeyboardMarkup([nav_buttons]).to_dict()
        await send_message(chat_id, f"📄 Страница {page} из {total_pages}", reply_markup=markup)
    else:
        await send_message(chat_id, f"📄 Страница {page} из {total_pages}")
