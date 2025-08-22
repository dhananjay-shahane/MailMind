import os
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import components
from config.config import Config
from api.email_processor import EmailProcessor
from api.function_registry import FunctionRegistry
from api.ollama_client import OllamaClient
from api.email_sender import EmailSender
from api.email_integration import EmailReceiver

# Import routes
from routes.main_routes import main_bp, init_routes
from routes.api_routes import api_bp, init_api_routes

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Initialize components
email_processor = EmailProcessor()
function_registry = FunctionRegistry()
ollama_client = OllamaClient()
email_sender = EmailSender()

# Register functions from all scripts
script_modules = [
    "scripts.sales_functions",
    "scripts.user_functions", 
    "scripts.analytics_functions",
    "scripts.system_functions",
    "scripts.finance_functions"
]

for module_name in script_modules:
    try:
        function_registry.register_module(module_name)
        logger.info(f"Registered functions from {module_name}")
    except Exception as e:
        logger.error(f"Failed to register functions from {module_name}: {e}")

# Store execution logs
execution_logs = []

# Initialize routes with dependencies
init_routes(function_registry, ollama_client, email_sender, execution_logs)
init_api_routes(function_registry, ollama_client, email_sender, email_processor, execution_logs)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)

# Initialize and start email receiver
email_receiver = None
try:
    email_receiver = EmailReceiver(function_registry, ollama_client, email_sender)
    email_receiver.start_monitoring()
    logger.info("Email receiver started successfully")
except Exception as e:
    logger.error(f"Failed to start email receiver: {e}")

if __name__ == '__main__':
    logger.info("Starting Email-to-Function Execution System")
    app.run(host='0.0.0.0', port=5000, debug=True)