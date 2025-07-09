import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# 🔐 Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# 🧠 OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "text-embedding-3-small"

# 🗃 Supabase
SUPABASE_URL = "https://iztwzgewaxzdmcbqkxlm.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_APIKEY")
SUPABASE_RPC_FUNCTION = "match_documents"
