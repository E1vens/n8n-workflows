from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Словарь для хранения языка пользователя
user_languages: dict[int, str] = {}

def set_user_language(chat_id: int, lang: str):
    user_languages[chat_id] = lang

def get_user_language(chat_id: int) -> str:
    return user_languages.get(chat_id, "ru")

async def handle_language_selection(chat_id: int, send_message):
    return await send_message(chat_id, "🌐 Выберите язык / Choose a language:", reply_markup=get_language_keyboard())

def get_language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang:es")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()

def get_translated_text(chat_id: int, text_id: str) -> str:
    lang = get_user_language(chat_id)
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

*Наш путь*:
- 1996: Основание компании и первые поставки вин Grand Cru.
- 1999: Дистрибуция Macallan.
- 2003: Первый бутик.
- 2004: Запуск ВЕЛЬД-СПб.
- 2006–2015: Контракт с Suntory на японский и шотландский виски.
- 2015: Новый склад с высоким стандартом хранения.
- 2016: Портфель 'Лучшие крепкие напитки мира'.
- 2021: Расширение ассортимента — самый большой выбор с 1996 года.

*Команда и обучение*:
Мы ценим профессионализм. Проводим лекции, туры, каталоги и обучающие курсы по алкоголю.

*Наш портфель*:
Импортируем лучшие продукты в своих категориях, большинство — на эксклюзивной основе.

📦 Подробнее: veld21.ru
📧 Партнёрство: info@veld-21.ru""",

            "en": """*About VELD-21*

A leading importer of strong alcohol, building brands for over 25 years.
Founded in 1996 — since then we have expanded our presence from Vladivostok to Kaliningrad, from Murmansk to Vladikavkaz.

• 1,000+ distributors in 87 key Russian cities — reaching over 56,000 outlets.
• Working with 50 federal and regional retail chains.
• Expert selection, personal approach, top suppliers, impeccable reputation.

*Our history*:
- 1996: Company founded, first Grand Cru wine shipments.
- 1999: Macallan distribution.
- 2003: First boutique.
- 2004: Launch of VELD-SPb.
- 2006–2015: Suntory contract for Japanese and Scotch whisky.
- 2015: New high-standard warehouse.
- 2016: ‘World’s Best Spirits’ portfolio.
- 2021: Expanded assortment — largest since 1996.

*Team & Education*:
We value professionalism. We host lectures, tastings, catalogs, and training courses on alcohol.

*Our portfolio*:
We import the best products in their categories, most on an exclusive basis.

📦 More: veld21.ru
📧 Partnerships: info@veld-21.ru""",

            "es": """*Sobre VELD-21*

Importador líder de alcohol fuerte, construyendo marcas desde hace más de 25 años.
Fundada en 1996 — desde entonces hemos expandido nuestra presencia desde Vladivostok hasta Kaliningrado, de Murmansk hasta Vladikavkaz.

• Más de 1.000 distribuidores en 87 ciudades clave de Rusia — con cobertura en más de 56.000 puntos de venta.
• Colaboramos con 50 cadenas minoristas federales y regionales.
• Selección experta, enfoque personalizado, proveedores líderes, reputación impecable.

*Nuestra historia*:
- 1996: Fundación de la empresa y primeros envíos de vinos Grand Cru.
- 1999: Distribución de Macallan.
- 2003: Primera boutique.
- 2004: Lanzamiento de VELD-SPb.
- 2006–2015: Contrato con Suntory para whisky japonés y escocés.
- 2015: Nuevo almacén con altos estándares.
- 2016: Portafolio ‘Los mejores licores del mundo’.
- 2021: Expansión del surtido — la mayor desde 1996.

*Equipo y educación*:
Valoramos el profesionalismo. Organizamos conferencias, recorridos, catálogos y formación sobre alcohol.

*Nuestro portafolio*:
Importamos los mejores productos en cada categoría, la mayoría en base exclusiva.

📦 Más: veld21.ru
📧 Asociación: info@veld-21.ru"""
        },

    }
    return translations.get(text_id, {}).get(lang, text_id)
