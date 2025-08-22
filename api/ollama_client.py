import requests
import json
import logging
from typing import List, Dict, Optional
from config.config import Config

logger = logging.getLogger(__name__)

class OllamaClient:
    """Simplified client for interacting with Ollama LLM - LLM manages function selection"""
    
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.OLLAMA_BASE_URL
        self.model = self.config.OLLAMA_MODEL
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except Exception:
            # Silently return False - no need to log every failure
            return False
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response from Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return None
    
    def identify_function(self, question: str, available_functions: List[Dict]) -> Optional[str]:
        """Use LLM to identify which function should handle the question with comprehensive mapping"""
        if not available_functions:
            logger.warning("No functions available")
            return None
        
        # Create detailed function mapping with keywords
        function_mapping = {
            "get_total_users": {
                "keywords": ["total users", "user count", "how many users", "registered users", "user statistics", "number of users", "user numbers", "user base", "total registered", "user breakdown"],
                "description": "Returns total number of registered users with breakdown and statistics"
            },
            "get_user_activity": {
                "keywords": ["user activity", "active users", "user engagement", "daily active", "weekly active", "session duration", "engagement rate", "user metrics"],
                "description": "Returns user activity metrics and engagement data"
            },
            "get_user_demographics": {
                "keywords": ["user demographics", "user age", "user location", "regional distribution", "age groups", "user regions", "demographic breakdown"],
                "description": "Returns user demographic breakdown and regional distribution"
            },
            "calculate_monthly_sales": {
                "keywords": ["monthly sales", "sales this month", "current month sales", "last month sales", "monthly revenue", "sales data", "monthly figures"],
                "description": "Returns total sales for a specific month"
            },
            "get_top_products": {
                "keywords": ["top products", "best selling products", "top selling", "best products", "popular products", "best performers", "product rankings"],
                "description": "Returns list of top selling products"
            },
            "calculate_sales_growth": {
                "keywords": ["sales growth", "growth rate", "sales increase", "growth percentage", "sales trend", "growth metrics", "sales comparison"],
                "description": "Returns sales growth percentage and trends"
            },
            "generate_traffic_report": {
                "keywords": ["traffic report", "website traffic", "page views", "visitors", "bounce rate", "traffic analytics", "web analytics"],
                "description": "Returns website traffic analytics report"
            },
            "get_conversion_metrics": {
                "keywords": ["conversion rate", "conversion metrics", "funnel analysis", "conversion data", "leads conversion", "trial conversion"],
                "description": "Returns conversion rates and funnel analysis"
            },
            "get_revenue_analytics": {
                "keywords": ["revenue analytics", "revenue breakdown", "revenue sources", "revenue forecast", "revenue data", "financial analytics"],
                "description": "Returns detailed revenue analytics and forecasting"
            },
            "generate_sales_chart": {
                "keywords": ["sales chart", "sales graph", "line chart", "sales trend chart", "monthly sales chart", "sales visualization"],
                "description": "Generates sales trend line chart"
            },
            "generate_user_analytics_chart": {
                "keywords": ["user chart", "user analytics chart", "pie chart", "user breakdown chart", "user pie chart", "analytics pie chart"],
                "description": "Generates user analytics pie chart"
            },
            "generate_revenue_chart": {
                "keywords": ["revenue chart", "revenue graph", "bar chart", "quarterly revenue", "revenue comparison", "revenue bar chart"],
                "description": "Generates revenue comparison bar chart"
            },
            "generate_system_metrics_chart": {
                "keywords": ["system metrics", "system chart", "performance chart", "cpu usage", "memory usage", "system performance"],
                "description": "Generates system metrics line chart"
            },
            "get_application_logs": {
                "keywords": ["application logs", "app logs", "system logs", "error logs", "log entries", "recent logs", "log data"],
                "description": "Returns recent application logs and error entries"
            },
            "get_database_metrics": {
                "keywords": ["database metrics", "db metrics", "database performance", "database stats", "db stats", "database health"],
                "description": "Returns database performance metrics and statistics"
            },
            "get_server_health": {
                "keywords": ["server health", "system health", "server status", "system status", "health check", "uptime"],
                "description": "Returns server health status and uptime information"
            },
            "calculate_financial_ratios": {
                "keywords": ["financial ratios", "financial metrics", "profit ratios", "financial analysis", "financial health"],
                "description": "Returns financial ratios and analysis metrics"
            },
            "calculate_profit_loss": {
                "keywords": ["profit loss", "p&l", "profit and loss", "earnings", "income statement", "financial results"],
                "description": "Returns profit and loss statement calculations"
            },
            "get_cash_flow": {
                "keywords": ["cash flow", "cash flow analysis", "liquidity", "cash position", "cash metrics"],
                "description": "Returns cash flow analysis and liquidity metrics"
            }
        }
        
        question_lower = question.lower()
        logger.info(f"🔍 Processing question: '{question}'")
        
        # Direct keyword matching first (most accurate)
        best_match = None
        highest_score = 0
        
        for func_name, mapping in function_mapping.items():
            score = 0
            matched_keywords = []
            
            for keyword in mapping["keywords"]:
                if keyword in question_lower:
                    score += len(keyword.split())  # Multi-word keywords get higher scores
                    matched_keywords.append(keyword)
            
            if score > highest_score:
                highest_score = score
                best_match = func_name
                logger.info(f"✅ Found keyword match: {func_name} (score: {score}, keywords: {matched_keywords})")
        
        if best_match and highest_score >= 1:
            logger.info(f"🎯 Direct keyword match selected: {best_match}")
            return best_match
        
        # Fallback to LLM with enhanced prompt
        prompt = f"""You are a function router. Given a user question, select the EXACT function name that best matches.

User Question: "{question}"

AVAILABLE FUNCTIONS AND THEIR PURPOSES:

USER FUNCTIONS:
- get_total_users: For questions about "total users", "how many users", "user count", "registered users"
- get_user_activity: For questions about "user activity", "active users", "engagement", "daily/weekly active"  
- get_user_demographics: For questions about "user demographics", "user age", "user location", "regional distribution"

SALES FUNCTIONS:
- calculate_monthly_sales: For questions about "monthly sales", "sales this month", "monthly revenue"
- get_top_products: For questions about "top products", "best selling", "popular products"
- calculate_sales_growth: For questions about "sales growth", "growth rate", "sales increase"

ANALYTICS FUNCTIONS:
- generate_traffic_report: For questions about "website traffic", "page views", "visitors", "bounce rate"
- get_conversion_metrics: For questions about "conversion rate", "funnel analysis", "conversion data"
- get_revenue_analytics: For questions about "revenue analytics", "revenue breakdown", "revenue sources"

CHART FUNCTIONS (only when user specifically asks for charts/graphs):
- generate_sales_chart: For "sales chart", "sales graph", "line chart" requests
- generate_user_analytics_chart: For "user chart", "pie chart", "user analytics chart" requests  
- generate_revenue_chart: For "revenue chart", "bar chart", "quarterly revenue chart" requests
- generate_system_metrics_chart: For "system metrics", "performance chart", "cpu/memory usage" requests

SYSTEM FUNCTIONS:
- get_application_logs: For questions about "logs", "errors", "application logs", "system logs"
- get_database_metrics: For questions about "database", "db metrics", "database performance"
- get_server_health: For questions about "server health", "system status", "uptime"

FINANCE FUNCTIONS:
- calculate_financial_ratios: For questions about "financial ratios", "financial metrics", "financial health"
- calculate_profit_loss: For questions about "profit loss", "p&l", "earnings", "income statement"  
- get_cash_flow: For questions about "cash flow", "liquidity", "cash position"

IMPORTANT RULES:
1. If user asks about "users" or "user count" → ALWAYS return "get_total_users"
2. If user asks about "sales" data → return "calculate_monthly_sales" or "get_top_products"
3. Only return chart functions when user explicitly asks for "chart", "graph", or "visualization"
4. Return ONLY the exact function name, nothing else

Function name:"""
        
        response = self.generate_response(prompt)
        logger.info(f"🤖 LLM Raw Response: '{response}'")
        
        if response:
            response = response.strip()
            
            # Find exact function names in the response
            function_names = [func['name'] for func in available_functions]
            for func_name in function_names:
                if func_name in response:
                    logger.info(f"✅ LLM identified function: {func_name}")
                    return func_name
            
            # Try exact lowercase matching
            response_lower = response.lower()
            for func in available_functions:
                if func['name'].lower() == response_lower:
                    logger.info(f"✅ LLM identified function (case insensitive): {func['name']}")
                    return func['name']
            
            logger.warning(f"❌ LLM response '{response}' did not match any function")
            return None
        else:
            logger.error("❌ LLM service failed to respond - check Ollama status")
            return None
    
