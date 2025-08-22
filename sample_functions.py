"""
Sample functions to demonstrate the email-to-function execution system.
These functions can be called via email by describing what you want to do.
"""

import random
from datetime import datetime, timedelta
import json

def calculate_total_sales(period="month"):
    """
    Calculate total sales for a given period.
    Returns mock sales data for demonstration.
    """
    # Mock sales data - in real implementation, this would query a database
    base_sales = 50000
    if period.lower() == "month":
        sales = base_sales + random.randint(-10000, 15000)
        return f"Total sales for this month: ${sales:,}"
    elif period.lower() == "week":
        sales = base_sales // 4 + random.randint(-2000, 3000)
        return f"Total sales for this week: ${sales:,}"
    elif period.lower() == "year":
        sales = base_sales * 12 + random.randint(-50000, 80000)
        return f"Total sales for this year: ${sales:,}"
    else:
        return f"Sales data not available for period: {period}"

def get_user_count():
    """
    Get the total number of registered users.
    Returns mock user count for demonstration.
    """
    # Mock user count - in real implementation, this would query a database
    user_count = random.randint(1200, 1500)
    return f"Total registered users: {user_count:,}"

def get_weather_info(location="New York"):
    """
    Get weather information for a specific location.
    Returns mock weather data for demonstration.
    """
    # Mock weather data - in real implementation, this would call a weather API
    temperatures = [68, 72, 75, 71, 69, 73, 76]
    conditions = ["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"]
    
    temp = random.choice(temperatures)
    condition = random.choice(conditions)
    
    return f"Weather in {location}: {temp}°F, {condition}"

def calculate_roi(investment, return_amount):
    """
    Calculate Return on Investment (ROI) percentage.
    Takes investment amount and return amount as parameters.
    """
    try:
        investment = float(investment)
        return_amount = float(return_amount)
        
        if investment <= 0:
            return "Investment amount must be greater than 0"
        
        roi = ((return_amount - investment) / investment) * 100
        return f"ROI: {roi:.2f}% (Investment: ${investment:,.2f}, Return: ${return_amount:,.2f})"
    
    except (ValueError, TypeError):
        return "Please provide valid numeric values for investment and return amounts"

def get_system_status():
    """
    Get current system status and health information.
    Returns system metrics and status.
    """
    uptime_hours = random.randint(24, 720)  # 1-30 days
    cpu_usage = random.randint(15, 85)
    memory_usage = random.randint(40, 90)
    
    status = {
        "status": "Running",
        "uptime": f"{uptime_hours} hours",
        "cpu_usage": f"{cpu_usage}%",
        "memory_usage": f"{memory_usage}%",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return f"System Status: {status['status']}\nUptime: {status['uptime']}\nCPU Usage: {status['cpu_usage']}\nMemory Usage: {status['memory_usage']}\nLast Updated: {status['last_updated']}"

def list_recent_orders(days=7):
    """
    List recent orders from the last N days.
    Returns mock order data for demonstration.
    """
    try:
        days = int(days)
        if days <= 0:
            days = 7
    except (ValueError, TypeError):
        days = 7
    
    # Mock order data
    order_count = random.randint(5, 25)
    total_value = random.randint(1000, 5000)
    
    return f"Recent orders (last {days} days):\n- Total orders: {order_count}\n- Total value: ${total_value:,}\n- Average order value: ${total_value/order_count:.2f}"

def convert_currency(amount, from_currency="USD", to_currency="EUR"):
    """
    Convert currency from one type to another.
    Returns converted amount using mock exchange rates.
    """
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return "Please provide a valid numeric amount"
    
    # Mock exchange rates - in real implementation, this would call a currency API
    exchange_rates = {
        "USD": {"EUR": 0.85, "GBP": 0.75, "JPY": 110},
        "EUR": {"USD": 1.18, "GBP": 0.88, "JPY": 130},
        "GBP": {"USD": 1.33, "EUR": 1.14, "JPY": 147}
    }
    
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency == to_currency:
        return f"{amount} {from_currency} = {amount} {to_currency}"
    
    if from_currency in exchange_rates and to_currency in exchange_rates[from_currency]:
        rate = exchange_rates[from_currency][to_currency]
        converted = amount * rate
        return f"{amount} {from_currency} = {converted:.2f} {to_currency} (Rate: {rate})"
    else:
        return f"Currency conversion not available for {from_currency} to {to_currency}"

def get_database_info():
    """
    Get database information and statistics.
    Returns mock database metrics.
    """
    tables = ["users", "orders", "products", "transactions", "logs"]
    table_counts = {table: random.randint(100, 10000) for table in tables}
    
    db_size = random.randint(50, 500)  # MB
    last_backup = datetime.now() - timedelta(hours=random.randint(1, 24))
    
    info = f"Database Information:\n"
    info += f"- Size: {db_size} MB\n"
    info += f"- Last backup: {last_backup.strftime('%Y-%m-%d %H:%M:%S')}\n"
    info += f"- Table counts:\n"
    
    for table, count in table_counts.items():
        info += f"  • {table}: {count:,} records\n"
    
    return info.strip()
