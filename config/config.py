import os

class Config:
    """Configuration settings for the email-to-function system"""
    
    # Ollama configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:1b')
    
    # Email configuration
    SMTP_HOST = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('MAIL_PORT', '587'))
    SMTP_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    SMTP_USERNAME = os.getenv('MAIL_USERNAME', 'dhanushahane01@gmail.com')
    SMTP_PASSWORD = os.getenv('MAIL_PASSWORD', 'sljo pinu ajrh padp')
    FROM_EMAIL = os.getenv('MAIL_DEFAULT_SENDER', 'dhanushahane01@gmail.com')
    EMAIL_USER = os.getenv('EMAIL_USER', 'dhanushahane01@gmail.com')
    
    # Security settings
    MAX_FUNCTION_EXECUTION_TIME = int(os.getenv('MAX_FUNCTION_EXECUTION_TIME', '30'))  # seconds
    ALLOWED_MODULES = os.getenv('ALLOWED_MODULES', 'scripts.sales_functions,scripts.user_functions,scripts.analytics_functions,scripts.system_functions,scripts.finance_functions').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
