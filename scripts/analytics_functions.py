"""
Analytics and reporting functions for the email-to-function execution system.
"""

import random
from datetime import datetime, timedelta

def generate_traffic_report():
    """
    Generate website traffic analytics report.
    Returns detailed traffic metrics and trends.
    """
    page_views = random.randint(15000, 25000)
    unique_visitors = random.randint(8000, 12000)
    bounce_rate = random.randint(25, 45)
    avg_duration = random.randint(180, 420)
    
    top_pages = [
        "/dashboard - 3,245 views",
        "/products - 2,890 views", 
        "/pricing - 2,156 views",
        "/about - 1,678 views",
        "/contact - 1,234 views"
    ]
    
    result = f"Website Traffic Report (Last 30 days):\n\n"
    result += f"📊 Key Metrics:\n"
    result += f"• Page Views: {page_views:,}\n"
    result += f"• Unique Visitors: {unique_visitors:,}\n"
    result += f"• Bounce Rate: {bounce_rate}%\n"
    result += f"• Avg. Session Duration: {avg_duration//60}m {avg_duration%60}s\n\n"
    result += f"🔝 Top Pages:\n" + "\n".join([f"• {page}" for page in top_pages])
    
    return result

def get_conversion_metrics():
    """
    Get conversion rates and funnel analysis.
    Returns conversion metrics across different stages.
    """
    visitors = random.randint(10000, 15000)
    leads = random.randint(1200, 1800)
    trials = random.randint(300, 600)
    customers = random.randint(80, 150)
    
    lead_conversion = (leads / visitors) * 100
    trial_conversion = (trials / leads) * 100
    customer_conversion = (customers / trials) * 100
    
    result = f"Conversion Funnel Analysis:\n\n"
    result += f"1. Visitors: {visitors:,}\n"
    result += f"2. Leads: {leads:,} ({lead_conversion:.1f}% conversion)\n"
    result += f"3. Trial Users: {trials:,} ({trial_conversion:.1f}% conversion)\n"
    result += f"4. Paying Customers: {customers:,} ({customer_conversion:.1f}% conversion)\n\n"
    result += f"🎯 Overall Conversion Rate: {(customers/visitors)*100:.2f}%"
    
    return result

def get_revenue_analytics():
    """
    Get detailed revenue analytics and forecasting.
    Returns revenue breakdown and predictions.
    """
    monthly_revenue = random.randint(45000, 75000)
    quarterly_revenue = monthly_revenue * 3 + random.randint(-5000, 15000)
    yearly_forecast = quarterly_revenue * 4 + random.randint(-20000, 50000)
    
    revenue_sources = {
        "Subscriptions": random.randint(60, 70),
        "One-time Sales": random.randint(20, 30),
        "Add-ons": random.randint(5, 15),
        "Consulting": random.randint(3, 8)
    }
    
    result = f"Revenue Analytics Report:\n\n"
    result += f"💰 Current Performance:\n"
    result += f"• Monthly Revenue: ${monthly_revenue:,}\n"
    result += f"• Quarterly Revenue: ${quarterly_revenue:,}\n"
    result += f"• Yearly Forecast: ${yearly_forecast:,}\n\n"
    result += f"📈 Revenue Sources:\n"
    result += "\n".join([f"• {source}: {percent}%" for source, percent in revenue_sources.items()])
    
    return result