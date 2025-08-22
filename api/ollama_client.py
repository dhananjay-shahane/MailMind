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
        """Use LLM to identify which function should handle the question - Pure AI approach"""
        if not available_functions:
            logger.warning("No functions available")
            return None
        
        logger.info(f"🤖 Processing question with LLM: '{question}'")
        
        # Use pure LLM identification with comprehensive training
        prompt = f"""You are an intelligent function router for a business analytics system. Your job is to understand the user's intent and select the correct function to execute.

TRAINING EXAMPLES - Learn from these patterns:

User Question: "Get the total number of registered users in the system"
Correct Answer: get_total_users
Reasoning: User wants user count/statistics

User Question: "I want revenue chart"  
Correct Answer: generate_revenue_chart
Reasoning: User specifically asked for a revenue chart/visualization

User Question: "Show me sales data"
Correct Answer: calculate_monthly_sales  
Reasoning: User wants sales information/data

User Question: "What are the top products"
Correct Answer: get_top_products
Reasoning: User wants product rankings/best sellers

User Question: "How many users are active"
Correct Answer: get_user_activity
Reasoning: User wants activity metrics, not just total count

User Question: "Show website traffic"
Correct Answer: generate_traffic_report
Reasoning: User wants traffic analytics/report

User Question: "I need profit and loss"
Correct Answer: calculate_profit_loss
Reasoning: User wants P&L financial data

CURRENT USER QUESTION: "{question}"

AVAILABLE FUNCTIONS:
"""

        # Add function list with descriptions
        for func in available_functions:
            prompt += f"- {func['name']}: {func['description']}\n"

        prompt += f"""
ANALYSIS INSTRUCTIONS:
1. Read the user question carefully
2. Identify the key intent (users, sales, charts, analytics, etc.)  
3. Match to the most appropriate function
4. If user asks about "total users", "user count", "how many users" → get_total_users
5. If user asks for "chart", "graph", "visualization" → use generate_* functions
6. If user asks about "sales" without specifying chart → calculate_monthly_sales
7. Consider the exact wording and context

Your answer must be ONLY the exact function name from the list above.

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
            return self._fallback_keyword_matching(question, available_functions)
        else:
            logger.error("❌ LLM service failed to respond - using fallback keyword matching")
            return self._fallback_keyword_matching(question, available_functions)
    
    def _fallback_keyword_matching(self, question: str, available_functions: List[Dict]) -> Optional[str]:
        """Fallback keyword matching when LLM is not available"""
        question_lower = question.lower()
        logger.info(f"🔍 Using fallback keyword matching for: '{question}'")
        
        # Simple but effective keyword mapping
        keyword_mapping = {
            'users': 'get_total_users',
            'user data': 'get_total_users', 
            'user count': 'get_total_users',
            'total users': 'get_total_users',
            'registered users': 'get_total_users',
            'user statistics': 'get_total_users',
            'how many users': 'get_total_users',
            'user activity': 'get_user_activity',
            'active users': 'get_user_activity',
            'user demographics': 'get_user_demographics',
            'sales': 'calculate_monthly_sales',
            'monthly sales': 'calculate_monthly_sales',
            'sales data': 'calculate_monthly_sales',
            'top products': 'get_top_products',
            'best selling': 'get_top_products',
            'sales growth': 'calculate_sales_growth',
            'growth rate': 'calculate_sales_growth',
            'traffic': 'generate_traffic_report',
            'website traffic': 'generate_traffic_report',
            'conversion': 'get_conversion_metrics',
            'conversion rate': 'get_conversion_metrics',
            'revenue analytics': 'get_revenue_analytics',
            'revenue data': 'get_revenue_analytics',
            'sales chart': 'generate_sales_chart',
            'revenue chart': 'generate_revenue_chart',
            'user chart': 'generate_user_analytics_chart',
            'pie chart': 'generate_user_analytics_chart',
            'system metrics': 'generate_system_metrics_chart',
            'logs': 'get_application_logs',
            'application logs': 'get_application_logs',
            'database metrics': 'get_database_metrics',
            'server health': 'get_server_health',
            'system health': 'get_server_health',
            'financial ratios': 'calculate_financial_ratios',
            'profit loss': 'calculate_profit_loss',
            'p&l': 'calculate_profit_loss',
            'cash flow': 'get_cash_flow'
        }
        
        # Check for keyword matches
        for keyword, function_name in keyword_mapping.items():
            if keyword in question_lower:
                # Verify the function exists in available functions
                for func in available_functions:
                    if func['name'] == function_name:
                        logger.info(f"✅ Fallback keyword match: '{keyword}' → {function_name}")
                        return function_name
        
        logger.warning(f"❌ No fallback keyword match found for: '{question}'")
        return None
    
