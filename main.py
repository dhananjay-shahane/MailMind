import os
import logging
from flask import Flask, render_template, jsonify, request
import threading
from datetime import datetime

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

# Create Flask app (no SocketIO to avoid crashes)
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
    "scripts.finance_functions",
    "scripts.chart_functions"
]

for module_name in script_modules:
    try:
        function_registry.register_module(module_name)
        logger.info(f"Registered functions from {module_name}")
    except Exception as e:
        logger.error(f"Failed to register functions from {module_name}: {e}")

# Store execution logs (global variable)
execution_logs = []

def log_execution(email_from, question, function_name, result, success=True, error=None):
    """Log function execution for monitoring"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'email_from': email_from,
        'question': question,
        'function_name': function_name,
        'result': str(result)[:500] if result else None,
        'success': success,
        'error': str(error) if error else None
    }
    execution_logs.append(log_entry)
    # Keep only last 100 logs
    if len(execution_logs) > 100:
        execution_logs.pop(0)

@app.route("/")
def dashboard():
    """Main dashboard showing system status and available functions"""
    available_functions = function_registry.get_available_functions()
    return render_template("index.html", 
                         functions=available_functions,
                         recent_logs=execution_logs[-10:])

@app.route("/logs")
def view_logs():
    """View execution logs"""
    return render_template("logs.html", logs=execution_logs)

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'functions_registered': len(function_registry.get_available_functions()),
        'ollama_available': ollama_client.is_available(),
        'total_logs': len(execution_logs)
    })

@app.route("/api/functions")
def get_functions():
    """Get available functions via API"""
    return jsonify(function_registry.get_available_functions())

@app.route("/api/execute", methods=["POST"])
def execute_function():
    """Execute a function via API"""
    try:
        data = request.get_json()
        function_name = data.get('function_name')
        question = data.get('question', '')
        
        if not function_name:
            return jsonify({"error": "function_name is required"}), 400
        
        result = function_registry.execute_function(function_name, question)
        log_execution("api", question, function_name, result, True)
        return jsonify({"success": True, "result": result})
        
    except Exception as e:
        log_execution("api", question if 'question' in locals() else "", 
                     function_name if 'function_name' in locals() else None, None, False, str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/webhook/email", methods=["POST"])
def email_webhook():
    """Webhook endpoint for processing emails"""
    try:
        data = request.get_json()
        
        # Process email
        email_data = email_processor.parse_email(data.get('raw_email', ''))
        if not email_data:
            return jsonify({"error": "Invalid email data"}), 400
        
        question = email_processor.extract_question(email_data['body'])
        if not question:
            return jsonify({"message": "No question found in email"})
        
        # Get available functions
        available_functions = function_registry.get_available_functions()
        
        # Use Ollama to identify function
        function_name = ollama_client.identify_function(question, available_functions)
        if not function_name:
            return jsonify({"message": "No appropriate function identified"})
        
        # Execute function
        result = function_registry.execute_function(function_name, question)
        
        # Log execution
        log_execution(email_data['from'], question, function_name, result, True)
        
        # Send email reply
        email_sender.send_response(email_data['from'], email_data.get('subject', ''), question, str(result))
        
        return jsonify({
            "success": True, 
            "function_executed": function_name,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error processing email webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/status")
def system_status():
    """Get real-time system status"""
    return jsonify({
        'email_monitoring': True,
        'ollama_available': ollama_client.is_available(),
        'functions_count': len(function_registry.get_available_functions()),
        'recent_logs_count': len(execution_logs),
        'last_log_time': execution_logs[-1]['timestamp'] if execution_logs else None
    })

# Initialize email receiver
email_receiver = None

def initialize_email_monitoring():
    """Initialize email monitoring"""
    global email_receiver
    try:
        email_receiver = EmailReceiver(function_registry, ollama_client, email_sender)
        email_receiver.start_monitoring()
        logger.info("Email receiver started successfully")
        
        # Try to start Ollama if not running
        try:
            if not ollama_client.is_available():
                logger.info("Checking Ollama service...")
                import subprocess
                subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.info(f"Ollama check: {e}")
            
    except Exception as e:
        logger.error(f"Failed to start email receiver: {e}")

# Start email monitoring in a separate thread
monitor_thread = threading.Thread(target=initialize_email_monitoring, daemon=True)
monitor_thread.start()

if __name__ == '__main__':
    logger.info("Starting Email-to-Function Execution System")
    app.run(host='0.0.0.0', port=5000, debug=False)