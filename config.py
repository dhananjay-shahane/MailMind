import os

class Config:
    """Configuration settings for the email-to-function system"""
    
    # Ollama configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
    
    # Email configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@example.com')
    
    # Security settings
    MAX_FUNCTION_EXECUTION_TIME = int(os.getenv('MAX_FUNCTION_EXECUTION_TIME', '30'))  # seconds
    ALLOWED_MODULES = os.getenv('ALLOWED_MODULES', 'sample_functions').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
