def escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы для Telegram MarkdownV2.
    """
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(['\\' + c if c in escape_chars else c for c in text])
