from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import OPENAI_API_KEY
import openai

# Установка API-ключа OpenAI
openai.api_key = OPENAI_API_KEY

# Словарь для хранения языка пользователя
user_languages: dict[int, str] = {}

def set_user_language(chat_id: int, lang: str):
    user_languages[chat_id] = lang

def get_user_language(chat_id: int) -> str:
    return user_languages.get(chat_id, "ru")

async def handle_language_selection(chat_id: int, send_message):
    return await send_message(
        chat_id,
        "🌐 Выберите язык / Choose a language:",
        reply_markup=get_language_keyboard()
    )

def get_language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang:es")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()

# Главный словарь переводов
translations = {
    "menu_prompt": {
        "ru": "Нажмите 🛍 Каталог",
        "en": "Press 🛍 Catalog",
        "es": "Presione 🛍 Catálogo",
    },
    "age_confirm": {
        "ru": "Подтвердите, пожалуйста, что вам есть 18 лет:",
        "en": "Please confirm that you are over 18:",
        "es": "Por favor confirme que tiene más de 18 años:",
    },
    "language_set": {
        "ru": "✅ Язык установлен: Русский",
        "en": "✅ Language set: English",
        "es": "✅ Idioma establecido: Español",
    },
    "no_categories": {
        "ru": "⚠️ Категории не найдены.",
        "en": "⚠️ No categories found.",
        "es": "⚠️ No se encontraron categorías.",
    },
    "select_category": {
        "ru": "📦 Выберите категорию товара:",
        "en": "📦 Choose a product category:",
        "es": "📦 Elija una categoría de producto:",
    },
    "unknown_category": {
        "ru": "⚠️ Неизвестная категория.",
        "en": "⚠️ Unknown category.",
        "es": "⚠️ Categoría desconocida.",
    },
    "empty_category": {
        "ru": "⚠️ В категории *{category}* ничего не найдено.",
        "en": "⚠️ No items found in *{category}*.",
        "es": "⚠️ No se encontraron artículos en *{category}*.",
    },
    "price": {"ru": "Цена", "en": "Price", "es": "Precio"},
    "volume": {"ru": "Объём", "en": "Volume", "es": "Volumen"},
    "strength": {"ru": "Крепость", "en": "Strength", "es": "Graduación"},
    "view_product": {
        "ru": "🔗 Открыть товар",
        "en": "🔗 View product",
        "es": "🔗 Ver producto",
    },
    "back": {"ru": "⬅️ Назад", "en": "⬅️ Back", "es": "⬅️ Atrás"},
    "next": {"ru": "➡️ Далее", "en": "➡️ Next", "es": "➡️ Siguiente"},
    "page_info": {
        "ru": "📄 Страница {page} из {total}",
        "en": "📄 Page {page} of {total}",
        "es": "📄 Página {page} de {total}",
    },
    "btn_age_yes": {
        "ru": "Да, мне есть 18",
        "en": "Yes, I'm over 18",
        "es": "Sí, tengo más de 18",
    },
    "btn_age_no": {
        "ru": "Нет",
        "en": "No",
        "es": "No",
    },
    "btn_catalog": {
        "ru": "Каталог",
        "en": "Catalog",
        "es": "Catálogo",
    },
    "btn_elite": {
        "ru": "Элитный алкоголь",
        "en": "Elite Alcohol",
        "es": "Alcohol Premium",
    },
    "btn_ai": {
        "ru": "ИИ консультант",
        "en": "AI Assistant",
        "es": "Asistente IA",
    },
    "btn_info": {
        "ru": "Информация о компании и партнёрах",
        "en": "Company Info",
        "es": "Información de la empresa",
    },
    "btn_language": {
        "ru": "Выбрать язык",
        "en": "Choose Language",
        "es": "Elegir idioma",
    },
    "btn_loyalty": {
        "ru": "Карта лояльности",
        "en": "Loyalty Card",
        "es": "Tarjeta de fidelidad",
    },
    "company_info": {
        "ru": """*О компании ВЕЛЬД-21*

Ведущий импортер крепкого алкоголя, строим бренды уже более 25 лет.
Основана в 1996 году — с тех пор мы расширили своё присутствие от Владивостока до Калининграда, от Мурманска до Владикавказа.

• Более 1000 дистрибьюторов в 87 ключевых городах РФ — охват 56 000+ торговых точек.
• Работаем с 50 федеральными и региональными сетями.
• Экспертный подбор, персональный подход, ведущие поставщики, безупречная репутация.

📦 Подробнее: veld21.ru
📧 Партнёрство: info@veld-21.ru"""
    }
}

# С автопереводом при отсутствии перевода
async def auto_translate_if_needed(chat_id: int, text_ru: str) -> str:
    lang = get_user_language(chat_id)
    if lang == "ru":
        return text_ru

    try:
        target_lang = {"en": "English", "es": "Spanish"}.get(lang, "English")

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Translate this text into {target_lang}. Preserve formatting and markdown."},
                {"role": "user", "content": text_ru}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ Ошибка перевода через GPT: {e}")
        return text_ru
