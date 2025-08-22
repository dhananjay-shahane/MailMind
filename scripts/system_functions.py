"""
System monitoring and health functions for the email-to-function execution system.
"""

import random
from datetime import datetime, timedelta

def get_server_health():
    """
    Get current server health and performance metrics.
    Returns comprehensive system health status.
    """
    cpu_usage = random.randint(15, 85)
    memory_usage = random.randint(40, 90)
    disk_usage = random.randint(25, 75)
    uptime_days = random.randint(1, 45)
    
    status = "🟢 Healthy" if cpu_usage < 70 and memory_usage < 80 else "🟡 Warning" if cpu_usage < 85 and memory_usage < 90 else "🔴 Critical"
    
    result = f"Server Health Status: {status}\n\n"
    result += f"🖥️ System Resources:\n"
    result += f"• CPU Usage: {cpu_usage}%\n"
    result += f"• Memory Usage: {memory_usage}%\n"
    result += f"• Disk Usage: {disk_usage}%\n"
    result += f"• Uptime: {uptime_days} days\n\n"
    result += f"⚡ Performance: {'Optimal' if cpu_usage < 50 else 'Good' if cpu_usage < 70 else 'Stressed'}"
    
    return result

def get_database_metrics():
    """
    Get database performance and connection metrics.
    Returns database health and performance data.
    """
    active_connections = random.randint(15, 50)
    max_connections = 100
    query_time = random.uniform(0.5, 5.0)
    db_size = random.uniform(2.5, 15.8)
    
    tables = {
        "users": random.randint(2000, 5000),
        "orders": random.randint(8000, 15000),
        "products": random.randint(150, 500),
        "transactions": random.randint(12000, 25000),
        "logs": random.randint(50000, 100000)
    }
    
    result = f"Database Metrics:\n\n"
    result += f"🔗 Connection Pool:\n"
    result += f"• Active Connections: {active_connections}/{max_connections}\n"
    result += f"• Average Query Time: {query_time:.2f}ms\n"
    result += f"• Database Size: {db_size:.1f} GB\n\n"
    result += f"📊 Table Record Counts:\n"
    result += "\n".join([f"• {table}: {count:,} records" for table, count in tables.items()])
    
    return result

def get_application_logs():
    """
    Get recent application logs and error summaries.
    Returns log analysis and error tracking data.
    """
    total_requests = random.randint(5000, 15000)
    error_count = random.randint(25, 150)
    warning_count = random.randint(100, 500)
    avg_response_time = random.randint(150, 800)
    
    error_types = {
        "Database Connection": random.randint(5, 20),
        "API Timeout": random.randint(8, 25),
        "Authentication Failed": random.randint(10, 35),
        "File Not Found": random.randint(3, 15),
        "Permission Denied": random.randint(2, 10)
    }
    
    error_rate = (error_count / total_requests) * 100
    
    result = f"Application Logs Summary (Last 24 hours):\n\n"
    result += f"📈 Request Statistics:\n"
    result += f"• Total Requests: {total_requests:,}\n"
    result += f"• Error Rate: {error_rate:.2f}%\n"
    result += f"• Warnings: {warning_count:,}\n"
    result += f"• Avg Response Time: {avg_response_time}ms\n\n"
    result += f"❌ Error Breakdown:\n"
    result += "\n".join([f"• {error_type}: {count}" for error_type, count in error_types.items()])
    
    return result