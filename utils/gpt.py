import os
from openai import AsyncOpenAI
from typing import List, Dict

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔮 Запрос к GPT
async def ask_gpt(messages: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

# 🧠 Ключевые слова по темам
SEARCH_KEYWORDS = [
    "цена", "стоимость", "почем", "сколько стоит", "дешево", "дорого",
    "виски", "водка", "вино", "коньяк", "шампанское", "ликер", "текила", "ром", "бренди", "алкоголь",
    "бутылка", "объем", "крепость", "градус", "крепкий", "слабоалкогольный",
    "найди", "подбери", "покажи", "подскажи", "каталог", "ассортимент", "есть ли", "наличие",
    "без сахара", "сладкий", "сухой", "белое", "красное", "напиток", "энергетик", "состав", "отзывы",
    "лучший", "популярный", "новинка", "фильтр", "сортировка", "по рейтингу", "по цене", "по объему"
]

COMPANY_KEYWORDS = [
    "о компании", "чем вы занимаетесь", "что за компания", "кто вы", "контакты", "адрес", "где вы",
    "работа", "вакансии", "как стать партнёром", "доставка", "оплата", "возврат", "гарантия",
    "условия", "юридическая информация", "сертификаты", "реквизиты", "история компании", "бренды",
    "наши поставщики", "ваши преимущества", "как работаете", "официально", "склад", "логистика"
]

CHAT_KEYWORDS = [
    "привет", "помоги", "подскажи", "расскажи", "не понимаю", "что делать", "порекомендуй",
    "задать вопрос", "общение", "чат", "можно спросить", "расскажи про", "подробнее"
]

# 🔍 Определение режима ИИ
def detect_ai_mode(message: str) -> str:
    text = message.lower()

    if any(word in text for word in SEARCH_KEYWORDS):
        return "search"
    elif any(word in text for word in COMPANY_KEYWORDS):
        return "company"
    elif any(word in text for word in CHAT_KEYWORDS):
        return "chat"
    else:
        return "chat"
