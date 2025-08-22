"""
Financial calculations and reporting functions for the email-to-function execution system.
"""

import random
from datetime import datetime, timedelta

def calculate_profit_loss():
    """
    Calculate profit and loss statement for current period.
    Returns detailed P&L breakdown with key metrics.
    """
    revenue = random.randint(80000, 120000)
    cost_of_goods = int(revenue * random.uniform(0.3, 0.5))
    operating_expenses = int(revenue * random.uniform(0.2, 0.35))
    marketing_costs = int(revenue * random.uniform(0.1, 0.2))
    
    gross_profit = revenue - cost_of_goods
    total_expenses = operating_expenses + marketing_costs
    net_profit = gross_profit - total_expenses
    
    profit_margin = (net_profit / revenue) * 100
    
    result = f"Profit & Loss Statement (Current Month):\n\n"
    result += f"💰 Revenue: ${revenue:,}\n"
    result += f"📦 Cost of Goods Sold: ${cost_of_goods:,}\n"
    result += f"📊 Gross Profit: ${gross_profit:,}\n\n"
    result += f"💼 Operating Expenses: ${operating_expenses:,}\n"
    result += f"📢 Marketing Costs: ${marketing_costs:,}\n"
    result += f"📉 Total Expenses: ${total_expenses:,}\n\n"
    result += f"🎯 Net Profit: ${net_profit:,}\n"
    result += f"📈 Profit Margin: {profit_margin:.1f}%"
    
    return result

def get_cash_flow():
    """
    Get cash flow analysis and liquidity position.
    Returns detailed cash flow statement and forecasts.
    """
    cash_inflow = random.randint(95000, 135000)
    cash_outflow = random.randint(70000, 110000)
    net_cash_flow = cash_inflow - cash_outflow
    
    current_cash = random.randint(50000, 200000)
    projected_cash = current_cash + net_cash_flow
    
    operating_cf = random.randint(40000, 80000)
    investing_cf = random.randint(-30000, -5000)
    financing_cf = random.randint(-15000, 25000)
    
    result = f"Cash Flow Analysis:\n\n"
    result += f"💵 Current Month:\n"
    result += f"• Cash Inflow: ${cash_inflow:,}\n"
    result += f"• Cash Outflow: ${cash_outflow:,}\n"
    result += f"• Net Cash Flow: ${net_cash_flow:,}\n\n"
    result += f"🏦 Cash Position:\n"
    result += f"• Current Cash: ${current_cash:,}\n"
    result += f"• Projected Cash: ${projected_cash:,}\n\n"
    result += f"📊 Cash Flow by Category:\n"
    result += f"• Operating: ${operating_cf:,}\n"
    result += f"• Investing: ${investing_cf:,}\n"
    result += f"• Financing: ${financing_cf:,}"
    
    return result

def calculate_financial_ratios():
    """
    Calculate key financial ratios and performance indicators.
    Returns comprehensive financial ratio analysis.
    """
    # Mock financial data
    current_assets = random.randint(150000, 300000)
    current_liabilities = random.randint(80000, 150000)
    total_assets = random.randint(400000, 800000)
    total_equity = random.randint(200000, 500000)
    annual_revenue = random.randint(800000, 1500000)
    net_income = random.randint(80000, 200000)
    
    # Calculate ratios
    current_ratio = current_assets / current_liabilities
    debt_to_equity = (total_assets - total_equity) / total_equity
    roi = (net_income / total_assets) * 100
    profit_margin = (net_income / annual_revenue) * 100
    
    result = f"Financial Ratios Analysis:\n\n"
    result += f"💧 Liquidity Ratios:\n"
    result += f"• Current Ratio: {current_ratio:.2f}\n"
    result += f"• Quick Ratio: {current_ratio * 0.8:.2f}\n\n"
    result += f"📊 Leverage Ratios:\n"
    result += f"• Debt-to-Equity: {debt_to_equity:.2f}\n"
    result += f"• Equity Ratio: {(total_equity/total_assets)*100:.1f}%\n\n"
    result += f"📈 Profitability Ratios:\n"
    result += f"• Return on Assets: {roi:.1f}%\n"
    result += f"• Profit Margin: {profit_margin:.1f}%\n"
    result += f"• Return on Equity: {(net_income/total_equity)*100:.1f}%"
    
    return result