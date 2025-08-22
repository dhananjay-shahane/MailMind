"""
Sales related functions for the email-to-function execution system.
"""

import random
from datetime import datetime, timedelta

def calculate_monthly_sales(month="current"):
    """
    Calculate total sales for a specific month.
    Returns sales data for the requested month.
    """
    base_sales = 75000
    if month.lower() in ["current", "this month"]:
        sales = base_sales + random.randint(-15000, 25000)
        return f"Monthly sales for current month: ${sales:,}"
    elif month.lower() in ["last month", "previous"]:
        sales = base_sales + random.randint(-10000, 20000)
        return f"Monthly sales for last month: ${sales:,}"
    else:
        sales = base_sales + random.randint(-20000, 30000)
        return f"Monthly sales for {month}: ${sales:,}"

def get_top_products():
    """
    Get list of top selling products.
    Returns the best performing products.
    """
    products = [
        "Wireless Headphones - $45,500",
        "Smart Watch - $38,200", 
        "Laptop Stand - $29,800",
        "USB-C Hub - $22,100",
        "Bluetooth Speaker - $19,600"
    ]
    return f"Top 5 selling products this month:\n" + "\n".join([f"{i+1}. {product}" for i, product in enumerate(products)])

def calculate_sales_growth():
    """
    Calculate sales growth percentage compared to last period.
    Returns growth metrics and trends.
    """
    current_sales = random.randint(70000, 90000)
    previous_sales = random.randint(60000, 80000)
    growth = ((current_sales - previous_sales) / previous_sales) * 100
    
    trend = "📈 Growing" if growth > 0 else "📉 Declining" if growth < -5 else "➡️ Stable"
    
    return f"Sales Growth Analysis:\nCurrent Period: ${current_sales:,}\nPrevious Period: ${previous_sales:,}\nGrowth Rate: {growth:.1f}%\nTrend: {trend}"