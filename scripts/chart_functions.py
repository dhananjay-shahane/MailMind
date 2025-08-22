import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import random
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# Configure matplotlib for white text on dark background
plt.style.use('dark_background')

def generate_sales_chart(question: str) -> str:
    """Generate sales trend chart in PNG format"""
    try:
        # Create charts directory if it doesn't exist
        os.makedirs('charts', exist_ok=True)
        
        # Generate realistic sales data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        sales_data = [
            45000 + random.randint(-5000, 8000) for _ in months
        ]
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#2d3748')  # Dark background
        ax.set_facecolor('#2d3748')
        
        # Plot the data
        line = ax.plot(months, sales_data, linewidth=3, color='#00ff88', marker='o', markersize=8)
        
        # Customize the chart with white text
        ax.set_title('Monthly Sales Trend 2024', fontsize=20, color='white', fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=14, color='white', fontweight='bold')
        ax.set_ylabel('Sales ($)', fontsize=14, color='white', fontweight='bold')
        
        # Format y-axis to show currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Customize grid and colors
        ax.grid(True, alpha=0.3, color='white')
        ax.tick_params(colors='white', labelsize=12)
        
        # Add value labels on points
        for i, v in enumerate(sales_data):
            ax.annotate(f'${v:,.0f}', (i, v), textcoords="offset points", 
                       xytext=(0,10), ha='center', fontsize=10, color='white', fontweight='bold')
        
        plt.tight_layout()
        
        # Save the chart
        filename = f'charts/sales_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#2d3748', edgecolor='none')
        plt.close()
        
        logger.info(f"Sales chart generated: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating sales chart: {e}")
        return None

def generate_user_analytics_chart(question: str) -> str:
    """Generate user analytics pie chart in PNG format"""
    try:
        os.makedirs('charts', exist_ok=True)
        
        # User category data
        categories = ['Active Users', 'New Users', 'Returning Users', 'Inactive Users']
        sizes = [1941, 88, 345, 214]
        colors = ['#00ff88', '#ff6b6b', '#4ecdc4', '#ffe66d']
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('#2d3748')
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=categories, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'color': 'white', 'fontsize': 12, 'fontweight': 'bold'})
        
        # Customize the chart
        ax.set_title('User Analytics Distribution', fontsize=20, color='white', fontweight='bold', pad=20)
        
        # Add total users annotation
        total_users = sum(sizes)
        ax.text(0, -1.3, f'Total Users: {total_users:,}', ha='center', fontsize=14, 
                color='white', fontweight='bold')
        
        plt.tight_layout()
        
        # Save the chart
        filename = f'charts/user_analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#2d3748', edgecolor='none')
        plt.close()
        
        logger.info(f"User analytics chart generated: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating user analytics chart: {e}")
        return None

def generate_revenue_chart(question: str) -> str:
    """Generate revenue comparison bar chart in PNG format"""
    try:
        os.makedirs('charts', exist_ok=True)
        
        # Revenue data by quarter
        quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
        revenue_2023 = [145000, 162000, 158000, 189000]
        revenue_2024 = [167000, 184000, 192000, 205000]
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#2d3748')
        ax.set_facecolor('#2d3748')
        
        # Bar positions
        x = np.arange(len(quarters))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar(x - width/2, revenue_2023, width, label='2023', color='#ff6b6b', alpha=0.8)
        bars2 = ax.bar(x + width/2, revenue_2024, width, label='2024', color='#00ff88', alpha=0.8)
        
        # Customize the chart
        ax.set_title('Quarterly Revenue Comparison', fontsize=20, color='white', fontweight='bold', pad=20)
        ax.set_xlabel('Quarter', fontsize=14, color='white', fontweight='bold')
        ax.set_ylabel('Revenue ($)', fontsize=14, color='white', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(quarters)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'${height:,.0f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=10, color='white', fontweight='bold')
        
        # Customize grid and colors
        ax.grid(True, alpha=0.3, color='white', axis='y')
        ax.tick_params(colors='white', labelsize=12)
        ax.legend(fontsize=12, facecolor='#2d3748', edgecolor='white', labelcolor='white')
        
        plt.tight_layout()
        
        # Save the chart
        filename = f'charts/revenue_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#2d3748', edgecolor='none')
        plt.close()
        
        logger.info(f"Revenue chart generated: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating revenue chart: {e}")
        return None

def generate_system_metrics_chart(question: str) -> str:
    """Generate system metrics line chart in PNG format"""
    try:
        os.makedirs('charts', exist_ok=True)
        
        # Generate time series data (last 24 hours)
        hours = [(datetime.now() - timedelta(hours=i)) for i in range(24, 0, -1)]
        cpu_usage = [random.randint(20, 85) for _ in range(24)]
        memory_usage = [random.randint(30, 90) for _ in range(24)]
        disk_usage = [random.randint(15, 60) for _ in range(24)]
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('#2d3748')
        ax.set_facecolor('#2d3748')
        
        # Plot the data
        ax.plot(hours, cpu_usage, linewidth=2, color='#ff6b6b', marker='o', markersize=4, label='CPU Usage (%)')
        ax.plot(hours, memory_usage, linewidth=2, color='#00ff88', marker='s', markersize=4, label='Memory Usage (%)')
        ax.plot(hours, disk_usage, linewidth=2, color='#4ecdc4', marker='^', markersize=4, label='Disk Usage (%)')
        
        # Customize the chart
        ax.set_title('System Metrics - Last 24 Hours', fontsize=20, color='white', fontweight='bold', pad=20)
        ax.set_xlabel('Time', fontsize=14, color='white', fontweight='bold')
        ax.set_ylabel('Usage (%)', fontsize=14, color='white', fontweight='bold')
        
        # Format x-axis to show time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.xticks(rotation=45)
        
        # Customize grid and colors
        ax.grid(True, alpha=0.3, color='white')
        ax.tick_params(colors='white', labelsize=12)
        ax.legend(fontsize=12, facecolor='#2d3748', edgecolor='white', labelcolor='white')
        
        # Set y-axis limits
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        
        # Save the chart
        filename = f'charts/system_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#2d3748', edgecolor='none')
        plt.close()
        
        logger.info(f"System metrics chart generated: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating system metrics chart: {e}")
        return None