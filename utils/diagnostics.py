### ✅ FILE: utils/embeddings.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_embedding(text: str) -> list[float]:
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=text
    )
    return response['data'][0]['embedding']


### ✅ FILE: utils/supabase.py
... (оставлено как есть)


### ✅ FILE: utils/gpt.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def ask_gpt(messages: list[dict], model="gpt-3.5-turbo") -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content


### ✅ FILE: diagnostics.py
import asyncio
from utils.supabase import set_ai_mode, get_ai_mode, clear_ai_mode, call_match_documents
from utils.embeddings import get_embedding
from utils.gpt import ask_gpt

async def run_diagnostics():
    chat_id = 123456789

    print("\n🔧 Тест 1: Установка и получение режима ИИ")
    set_ai_mode(chat_id, "chat")
    mode = get_ai_mode(chat_id)
    print("👉 Полученный режим:", mode)

    print("\n🔧 Тест 2: Получение embedding и поиск документов")
    query = "что-нибудь сладкое до 1000"
    embedding = await get_embedding(query)
    results = call_match_documents(embedding)
    if results:
        print(f"👉 Найдено товаров: {len(results)}")
        for r in results:
            print(f"- {r['title']} • {r['price']}₽")
    else:
        print("❌ Товары не найдены")

    print("\n🔧 Тест 3: GPT-ответ в режиме FAQ")
    messages = [
        {"role": "system", "content": "Ты консультант по алкоголю, отвечай строго по делу."},
        {"role": "user", "content": "Можно ли хранить водку в морозилке?"}
    ]
    reply = await ask_gpt(messages)
    print("👉 Ответ GPT:", reply)

    print("\n✅ Диагностика завершена")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
