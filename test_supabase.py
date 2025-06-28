from utils.supabase import get_distinct_categories

print("🔍 Получаем категории из Supabase...")
categories = get_distinct_categories()
print("📦 Категории:", categories)
