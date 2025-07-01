import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def ask_gpt(messages: list[dict], model="gpt-3.5-turbo") -> str:
    response = openai.ChatCompletion.acreate(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content
