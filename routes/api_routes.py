from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Will be set by app initialization
function_registry = None
ollama_client = None
email_sender = None
email_processor = None
execution_logs = []

def init_api_routes(func_registry, ollama_cli, email_snd, email_proc, exec_logs):
    """Initialize API routes with dependencies"""
    global function_registry, ollama_client, email_sender, email_processor, execution_logs
    function_registry = func_registry
    ollama_client = ollama_cli
    email_sender = email_snd
    email_processor = email_proc
    execution_logs = exec_logs

def log_execution(email_from, question, function_name, result, success=True, error=None):
    """Log function execution for monitoring"""
    from datetime import datetime
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
    if len(execution_logs) > 100:
        execution_logs.pop(0)

@api_bp.route('/functions')
def get_functions():
    """API endpoint to get available functions"""
    return jsonify(function_registry.get_available_functions())

@api_bp.route('/logs')
def get_logs():
    """API endpoint to get execution logs"""
    return jsonify(execution_logs)

@api_bp.route('/webhook/email', methods=['POST'])
def email_webhook():
    """Email webhook endpoint for processing incoming emails"""
    try:
        logger.info(f"Received webhook request from {request.remote_addr}")
        
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Extract email components
        email_from = data.get('from', 'unknown@example.com')
        email_subject = data.get('subject', 'No Subject')
        email_body = data.get('body', '')
        
        logger.info(f"Processing email from {email_from} with subject: {email_subject}")
        
        # Extract question from email body
        question = email_processor.extract_question(email_body)
        if not question:
            error_msg = "Could not extract a valid question from email body"
            logger.warning(error_msg)
            log_execution(email_from, email_body[:100], None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
            
        logger.info(f"Extracted question: {question}")
        
        # Get available functions and let LLM identify the right one
        available_functions = function_registry.get_available_functions()
        function_name = ollama_client.identify_function(question, available_functions)
        
        if not function_name:
            error_msg = "LLM could not identify appropriate function for the question"
            logger.warning(error_msg)
            log_execution(email_from, question, None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
            
        logger.info(f"LLM identified function: {function_name}")
        
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

@api_bp.route('/process-email/dhanushahane01@gmail.com', methods=['POST'])
def process_dhanush_email():
    """Special endpoint for processing emails sent to dhanushahane01@gmail.com"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        target_email = "dhanushahane01@gmail.com"
        email_from = data.get('from', 'unknown@example.com')
        email_subject = data.get('subject', 'No Subject')
        email_body = data.get('body', '')
        
        logger.info(f"Processing email TO {target_email} FROM {email_from}")
        
        # Extract question and let LLM handle function selection
        question = email_processor.extract_question(email_body)
        if not question:
            error_msg = "Could not extract a valid question from email body"
            log_execution(email_from, email_body[:100], None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
        
        # LLM identifies and executes function
        available_functions = function_registry.get_available_functions()
        function_name = ollama_client.identify_function(question, available_functions)
        
        if not function_name:
            error_msg = "LLM could not identify appropriate function"
            log_execution(email_from, question, None, None, False, error_msg)
            return jsonify({'error': error_msg}), 400
        
        result = function_registry.execute_function(function_name, question)
        response_sent = email_sender.send_response(email_from, email_subject, question, result)
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