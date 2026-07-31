"""
Utility Formatters
"""
from datetime import datetime


def format_number(value: float, decimals: int = 2) -> str:
    if value >= 1000000:
        return f"{value/1000000:.{decimals}f}M"
    if value >= 1000:
        return f"{value/1000:.{decimals}f}K"
    return f"{value:.{decimals}f}"

def format_currency(value: float, currency: str = "USD") -> str:
    symbols = {"USD": "$", "EUR": "€", "BRL": "R$"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{value:,.2f}"

def format_percentage(value: float) -> str:
    return f"{value:.1f}%"

def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    return date.strftime(format_str)

def format_relative_time(date: datetime) -> str:
    delta = datetime.now() - date
    if delta.days > 365:
        return f"{delta.days // 365}y ago"
    if delta.days > 30:
        return f"{delta.days // 30}mo ago"
    if delta.days > 0:
        return f"{delta.days}d ago"
    if delta.seconds > 3600:
        return f"{delta.seconds // 3600}h ago"
    if delta.seconds > 60:
        return f"{delta.seconds // 60}m ago"
    return "just now"

def truncate(text: str, length: int = 100) -> str:
    if len(text) <= length:
        return text
    return text[:length-3] + "..."

def slugify(text: str) -> str:
    return text.lower().replace(" ", "-").replace("_", "-")
