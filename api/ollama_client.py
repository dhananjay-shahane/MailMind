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
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
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
        """Use LLM to identify which function should handle the question - No Python fallbacks"""
        if not available_functions:
            logger.warning("No functions available")
            return None
        
        # Create function list for the prompt
        functions_text = "\n".join([
            f"- {func['name']}: {func['description']}"
            for func in available_functions
        ])
        
        prompt = f"""You are a business function dispatcher. Your job is to analyze user questions and select the most appropriate function to execute.

Available business functions:
{functions_text}

User question: "{question}"

Analyze the question and determine which function would best answer it. Consider:
- Keywords related to sales, revenue, money → sales functions
- Keywords related to users, customers, accounts → user functions  
- Keywords related to reports, analytics, traffic → analytics functions
- Keywords related to server, system, health → system functions
- Keywords related to profit, finance, cash → finance functions

Respond with ONLY the exact function name that matches best. If no function is appropriate, respond with "NONE".

Function name:"""
        
        logger.info(f"Sending function identification request to LLM")
        
        response = self.generate_response(prompt)
        if not response:
            logger.warning("No response from LLM for function identification")
            return None
        
        # Clean up the response
        function_name = response.strip().lower()
        
        # Check if the response matches any available function
        for func in available_functions:
            if func['name'].lower() == function_name:
                logger.info(f"LLM identified function: {func['name']}")
                return func['name']
        
        # Check for partial matches
        for func in available_functions:
            if function_name in func['name'].lower() or func['name'].lower() in function_name:
                logger.info(f"LLM identified function (partial match): {func['name']}")
                return func['name']
        
        logger.warning(f"LLM response '{response}' did not match any function")
        return None