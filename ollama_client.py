import requests
import json
import logging
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama LLM"""
    
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
        """Use LLM to identify which function should handle the question"""
        if not available_functions:
            return None
        
        # Create function list for the prompt
        functions_text = "\n".join([
            f"- {func['name']}: {func['description']}"
            for func in available_functions
        ])
        
        prompt = f"""You are a helpful assistant that maps user questions to appropriate functions.

Available functions:
{functions_text}

User question: "{question}"

Based on the user's question, which function would be most appropriate to answer it?
Respond with ONLY the function name, nothing else. If no function is appropriate, respond with "NONE".

Function name:"""
        
        logger.info(f"Sending prompt to Ollama: {prompt[:200]}...")
        
        response = self.generate_response(prompt)
        if not response:
            logger.warning("No response from Ollama")
            return self._fallback_function_matching(question, available_functions)
        
        # Clean up the response
        function_name = response.strip().lower()
        
        # Check if the response matches any available function
        for func in available_functions:
            if func['name'].lower() == function_name:
                logger.info(f"Ollama identified function: {func['name']}")
                return func['name']
        
        # If exact match not found, try partial matching
        for func in available_functions:
            if function_name in func['name'].lower() or func['name'].lower() in function_name:
                logger.info(f"Ollama identified function (partial match): {func['name']}")
                return func['name']
        
        logger.warning(f"Ollama response '{response}' did not match any function")
        return self._fallback_function_matching(question, available_functions)
    
    def _fallback_function_matching(self, question: str, available_functions: List[Dict]) -> Optional[str]:
        """Fallback function matching using simple keyword matching"""
        logger.info("Using fallback function matching")
        
        question_lower = question.lower()
        
        # Simple keyword matching
        for func in available_functions:
            func_name_lower = func['name'].lower()
            func_desc_lower = func['description'].lower()
            
            # Check if question contains function name or key terms from description
            if func_name_lower in question_lower:
                return func['name']
            
            # Extract key terms from function description
            key_terms = []
            if 'sales' in func_desc_lower:
                key_terms.extend(['sales', 'revenue', 'sold'])
            if 'user' in func_desc_lower:
                key_terms.extend(['user', 'customer', 'account'])
            if 'total' in func_desc_lower:
                key_terms.extend(['total', 'sum', 'count'])
            if 'weather' in func_desc_lower:
                key_terms.extend(['weather', 'temperature', 'forecast'])
            if 'calculate' in func_desc_lower:
                key_terms.extend(['calculate', 'compute', 'math'])
            
            # Check if any key terms match
            if any(term in question_lower for term in key_terms):
                return func['name']
        
        # If no match found, return the first function as a last resort
        if available_functions:
            logger.warning(f"No good match found, defaulting to first function: {available_functions[0]['name']}")
            return available_functions[0]['name']
        
        return None
