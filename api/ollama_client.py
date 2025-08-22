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
        """Use LLM to identify which function should handle the question - Pure LLM approach"""
        if not available_functions:
            logger.warning("No functions available")
            return None
        
        # Create function list for the prompt
        functions_text = "\n".join([
            f"- {func['name']}: {func['description']}"
            for func in available_functions
        ])
        
        prompt = f"""Question: "{question}"

Available functions:
{functions_text}

Keywords guide:
"pie chart" -> generate_user_analytics_chart
"line chart" -> generate_sales_chart
"bar chart" -> generate_revenue_chart
"sales growth" -> calculate_sales_growth
"total users" -> get_total_users
"traffic report" -> generate_traffic_report

Choose the best matching function name:"""
        
        logger.info(f"Sending function identification request to LLM")
        logger.info(f"🔍 LLM Prompt: {prompt[:300]}...")
        
        response = self.generate_response(prompt)
        logger.info(f"🤖 LLM Raw Response: '{response}'")
        
        if response:
            response = response.strip()
            
            # First, try to find exact function names in the response
            function_names = [func['name'] for func in available_functions]
            for func_name in function_names:
                if func_name in response:
                    logger.info(f"✅ LLM identified function: {func_name}")
                    return func_name
            
            # If no exact match, try lowercase matching
            function_name = response.lower()
            for func in available_functions:
                if func['name'].lower() == function_name:
                    logger.info(f"✅ LLM identified function: {func['name']}")
                    return func['name']
            
            # Try partial matches as last resort  
            for func in available_functions:
                if function_name in func['name'].lower() or func['name'].lower() in function_name:
                    logger.info(f"✅ LLM identified function (partial match): {func['name']}")
                    return func['name']
            
            logger.warning(f"❌ LLM response '{response}' did not match any function")
            return None
        else:
            logger.error("❌ LLM service failed to respond - check Ollama status")
            return None
    
