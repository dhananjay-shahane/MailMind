import os
import logging
from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
from datetime import datetime
import json

from email_processor import EmailProcessor
from function_registry import FunctionRegistry
from ollama_client import OllamaClient
from email_sender import EmailSender
from email_integration import EmailReceiver

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Initialize components
email_processor = EmailProcessor()
function_registry = FunctionRegistry()
ollama_client = OllamaClient()
email_sender = EmailSender()

# Initialize email receiver (will start monitoring in background)
email_receiver = None

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

# Initialize and start email receiver
try:
    email_receiver = EmailReceiver(function_registry, ollama_client, email_sender)
    email_receiver.start_monitoring()
    logger.info("Email receiver started successfully")
except Exception as e:
    logger.error(f"Failed to start email receiver: {e}")

# Store execution logs
execution_logs = []

def log_execution(email_from, question, function_name, result, success=True, error=None):
    """Log function execution for monitoring"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'email_from': email_from,
        'question': question,
        'function_name': function_name,
        'result': str(result)[:500] if result else None,  # Truncate long results
        'success': success,
        'error': str(error) if error else None
    }
    execution_logs.append(log_entry)
    # Keep only last 100 logs
    if len(execution_logs) > 100:
        execution_logs.pop(0)

@app.route('/')
def index():
    """Main dashboard showing system status and available functions"""
    available_functions = function_registry.get_available_functions()
    return render_template('index.html', 
                         functions=available_functions,
                         recent_logs=execution_logs[-10:])

@app.route('/webhook/email', methods=['POST'])
def email_webhook():
    """
    Webhook endpoint to receive email content
    Expected format: JSON with 'from', 'subject', 'body' fields
    """
    try:
        # Log the incoming request
        logger.info(f"Received webhook request from {request.remote_addr}")
        
        # Get JSON data from request
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Extract email components
        email_from = data.get('from', 'unknown@example.com')
        email_subject = data.get('subject', 'No Subject')
        email_body = data.get('body', '')
        
        logger.info(f"Processing email from {email_from} with subject: {email_subject}")
        
        # Parse the email to extract the question
        question = email_processor.extract_question(email_body)
        if not question:
            error_msg = "Could not extract a valid question from email body"
            logger.warning(error_msg)
            log_execution(email_from, email_body[:100], None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
            
        logger.info(f"Extracted question: {question}")
        
        # Get available functions for context
        available_functions = function_registry.get_available_functions()
        
        # Use Ollama to determine which function to call
        function_name = ollama_client.identify_function(question, available_functions)
        if not function_name:
            error_msg = "Could not identify appropriate function for the question"
            logger.warning(error_msg)
            log_execution(email_from, question, None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
            
        logger.info(f"Identified function: {function_name}")
        
        # Execute the function
        try:
            result = function_registry.execute_function(function_name, question)
            logger.info(f"Function execution successful: {result}")
            
            # Send email response
            response_sent = email_sender.send_response(email_from, email_subject, question, result)
            
            # Log successful execution
            log_execution(email_from, question, function_name, result, True)
            
            return jsonify({
                'success': True,
                'function_executed': function_name,
                'result': result,
                'email_sent': response_sent
            })
            
        except Exception as func_error:
            error_msg = f"Error executing function {function_name}: {str(func_error)}"
            logger.error(error_msg)
            log_execution(email_from, question, function_name, None, False, func_error)
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Email processing endpoint specifically for dhanushahane01@gmail.com
@app.route('/process-email/dhanushahane01@gmail.com', methods=['POST'])
def process_dhanush_email():
    """
    Special endpoint for processing emails sent to dhanushahane01@gmail.com
    This simulates receiving an email to that specific address
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Set the target email address
        target_email = "dhanushahane01@gmail.com"
        email_from = data.get('from', 'unknown@example.com')
        email_subject = data.get('subject', 'No Subject')
        email_body = data.get('body', '')
        
        logger.info(f"Processing email TO {target_email} FROM {email_from} with subject: {email_subject}")
        
        # Extract question from email body
        question = email_processor.extract_question(email_body)
        if not question:
            error_msg = "Could not extract a valid question from email body"
            logger.warning(error_msg)
            log_execution(email_from, email_body[:100], None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Get available functions and identify the right function
        available_functions = function_registry.get_available_functions()
        function_name = ollama_client.identify_function(question, available_functions)
        
        if not function_name:
            error_msg = "Could not identify appropriate function for the question"
            logger.warning(error_msg)
            log_execution(email_from, question, None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Execute the identified function
        result = function_registry.execute_function(function_name, question)
        logger.info(f"Function {function_name} executed successfully: {result}")
        
        # Send email response back to the sender
        response_sent = email_sender.send_response(email_from, email_subject, question, result)
        
        # Log the execution
        log_execution(email_from, question, function_name, result, True)
        
        return jsonify({
            "success": True,
            "target_email": target_email,
            "from_email": email_from,
            "function_executed": function_name,
            "result": result,
            "email_response_sent": response_sent
        })
        
    except Exception as e:
        logger.error(f"Error processing email for dhanushahane01@gmail.com: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/test', methods=['GET', 'POST'])
def test_function():
    """Test endpoint to manually test function execution"""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            flash('Please enter a question', 'error')
            return redirect(url_for('test_function'))
            
        try:
            # Get available functions
            available_functions = function_registry.get_available_functions()
            
            # Use Ollama to identify function
            function_name = ollama_client.identify_function(question, available_functions)
            if not function_name:
                flash('Could not identify appropriate function for the question', 'error')
                return redirect(url_for('test_function'))
                
            # Execute function
            result = function_registry.execute_function(function_name, question)
            
            # Log execution
            log_execution('test@system.local', question, function_name, result, True)
            
            flash(f'Function "{function_name}" executed successfully!', 'success')
            flash(f'Result: {result}', 'info')
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            
        return redirect(url_for('test_function'))
    
    return render_template('index.html', 
                         functions=function_registry.get_available_functions(),
                         recent_logs=execution_logs[-10:],
                         show_test=True)

@app.route('/logs')
def view_logs():
    """View execution logs"""
    return render_template('logs.html', logs=execution_logs)

@app.route('/api/functions')
def api_functions():
    """API endpoint to get available functions"""
    return jsonify(function_registry.get_available_functions())

@app.route('/api/logs')
def api_logs():
    """API endpoint to get execution logs"""
    return jsonify(execution_logs)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'functions_registered': len(function_registry.get_available_functions()),
        'ollama_available': ollama_client.is_available(),
        'email_receiver_running': email_receiver.running if email_receiver else False
    })

@app.route('/start-email-monitoring', methods=['POST'])
def start_email_monitoring():
    """Manually start email monitoring"""
    global email_receiver
    try:
        if not email_receiver:
            email_receiver = EmailReceiver(function_registry, ollama_client, email_sender)
        
        if not email_receiver.running:
            email_receiver.start_monitoring()
            return jsonify({'success': True, 'message': 'Email monitoring started'})
        else:
            return jsonify({'success': False, 'message': 'Email monitoring already running'})
            
    except Exception as e:
        logger.error(f"Failed to start email monitoring: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/stop-email-monitoring', methods=['POST'])
def stop_email_monitoring():
    """Manually stop email monitoring"""
    global email_receiver
    try:
        if email_receiver and email_receiver.running:
            email_receiver.stop_monitoring()
            return jsonify({'success': True, 'message': 'Email monitoring stopped'})
        else:
            return jsonify({'success': False, 'message': 'Email monitoring not running'})
            
    except Exception as e:
        logger.error(f"Failed to stop email monitoring: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Email-to-Function Execution System with Flask")
    app.run(host='0.0.0.0', port=5000, debug=True)