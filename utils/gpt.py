import os
from openai import AsyncOpenAI
from typing import List, Dict

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 💬 Ответ от GPT в режиме чата
async def ask_gpt(messages: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content.strip()

# 🔮 Определение режима через GPT
async def detect_ai_mode_gpt(message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Ты ассистент, который определяет намерение пользователя на основе его сообщения.\n"
                "Ты должен выбрать одну из трёх чётких категорий:\n\n"
                "1. `search` — если пользователь хочет найти или подобрать товар. Например, если он:\n"
                "- просит показать ассортимент, список, категории,\n"
                "- указывает цену, объём, крепость, фильтры,\n"
                "- использует фразы вроде: «водка до 1000», «покажи шампанское», «ищу текилу», «что есть».\n\n"
                "2. `chat` — если пользователь ведёт свободный диалог, обсуждает конкретный товар, задаёт вопросы без фильтров или просто болтает.\n"
                "Это включает:\n"
                "- «что скажешь об этой водке», «ты пробовал этот ром», «что лучше выбрать»,\n"
                "- приветствия, прощания, шутки, вопросы общего характера.\n\n"
                "3. `company` — если речь идёт об информации о магазине: доставка, возврат, контакты, лицензии, регионы, реквизиты, партнёрство.\n\n"
                "Ответь только одним словом: `search`, `chat`, или `company`. Никаких пояснений."
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
    return response.choices[0].message.content.strip().lower()
