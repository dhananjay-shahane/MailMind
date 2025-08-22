"""
User management functions for the email-to-function execution system.
"""

import random
from datetime import datetime, timedelta

def get_total_users():
    """
    Get the total number of registered users in the system.
    Returns current user count with breakdown.
    """
    total_users = random.randint(2500, 3500)
    active_users = int(total_users * 0.75)
    new_users = random.randint(50, 150)
    
    return f"User Statistics:\nTotal Users: {total_users:,}\nActive Users: {active_users:,}\nNew Users (this month): {new_users:,}\nGrowth Rate: +{new_users/total_users*100:.1f}%"

def get_user_activity():
    """
    Get user activity metrics and engagement data.
    Returns detailed user engagement statistics.
    """
    daily_active = random.randint(800, 1200)
    weekly_active = random.randint(1500, 2200)
    avg_session = random.randint(15, 45)
    
    return f"User Activity Metrics:\nDaily Active Users: {daily_active:,}\nWeekly Active Users: {weekly_active:,}\nAverage Session Duration: {avg_session} minutes\nEngagement Rate: {(daily_active/weekly_active*100):.1f}%"

def get_user_demographics():
    """
    Get user demographic breakdown and regional distribution.
    Returns user demographics and location data.
    """
    regions = {
        "North America": random.randint(40, 50),
        "Europe": random.randint(25, 35), 
        "Asia": random.randint(15, 25),
        "Other": random.randint(5, 10)
    }
    
    age_groups = {
        "18-25": random.randint(20, 30),
        "26-35": random.randint(35, 45),
        "36-50": random.randint(20, 30),
        "50+": random.randint(5, 15)
    }
    
    result = "User Demographics:\n\nRegional Distribution:\n"
    result += "\n".join([f"• {region}: {percent}%" for region, percent in regions.items()])
    result += "\n\nAge Distribution:\n"
    result += "\n".join([f"• {age}: {percent}%" for age, percent in age_groups.items()])
    
    return result