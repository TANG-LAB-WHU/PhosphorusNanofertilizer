"""
Currency Utilities Module

Currency formatting and conversion utilities.
"""

from typing import Optional


def format_currency(
    value: float,
    currency: str = "USD",
    precision: int = 2
) -> str:
    """
    Format a value as currency string.
    
    Args:
        value: Numeric value
        currency: Currency code (USD, EUR, CNY)
        precision: Decimal places
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "CNY": "¥",
        "GBP": "£",
    }
    
    symbol = symbols.get(currency, currency + " ")
    
    if abs(value) >= 1_000_000:
        return f"{symbol}{value/1_000_000:,.{precision}f}M"
    elif abs(value) >= 1_000:
        return f"{symbol}{value/1_000:,.{precision}f}K"
    else:
        return f"{symbol}{value:,.{precision}f}"


def format_currency_full(
    value: float,
    currency: str = "USD",
    precision: int = 2
) -> str:
    """
    Format a value as full currency string (no abbreviation).
    
    Args:
        value: Numeric value
        currency: Currency code
        precision: Decimal places
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "CNY": "¥",
        "GBP": "£",
    }
    
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{value:,.{precision}f}"


# Exchange rates (base: USD, as of 2024)
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "CNY": 7.25,
    "GBP": 0.79,
    "JPY": 150.0,
    "INR": 83.0,
}


def convert_currency(
    value: float,
    from_currency: str,
    to_currency: str
) -> float:
    """
    Convert currency value.
    
    Args:
        value: Value in source currency
        from_currency: Source currency code
        to_currency: Target currency code
        
    Returns:
        Value in target currency
    """
    if from_currency == to_currency:
        return value
    
    # Convert to USD first
    from_rate = EXCHANGE_RATES.get(from_currency, 1.0)
    to_rate = EXCHANGE_RATES.get(to_currency, 1.0)
    
    usd_value = value / from_rate
    return usd_value * to_rate


if __name__ == "__main__":
    # Example usage
    print(format_currency(1234567.89))
    print(format_currency(1234.56))
    print(format_currency(123.45))
    print(convert_currency(100, "USD", "EUR"))
