import os
from openai import AsyncOpenAI
from typing import List, Dict

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔮 Запрос к GPT
async def detect_ai_mode_gpt(message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Ты классификатор входящих сообщений.\n"
                "У тебя есть три возможных категории:\n"
                "1. search — если пользователь ищет товар, интересуется ценой, фильтрацией или характеристиками.\n"
                "2. company — если пользователь спрашивает о компании, услугах, доставке, контактах, партнёрстве и т.п.\n"
                "3. chat — всё остальное: просто общение, приветствие, помощь, фразы вне тематики.\n\n"
                "Отвечай только одной категорией: `search`, `company` или `chat`."
            )
        },
        {
            "role": "user",
            "content": message
        }
    ]

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content.strip()


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
