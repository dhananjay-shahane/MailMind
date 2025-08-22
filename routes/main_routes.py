from flask import Blueprint, request, render_template, jsonify, flash, redirect, url_for
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Will be set by app initialization
function_registry = None
ollama_client = None
email_sender = None
execution_logs = []

def init_routes(func_registry, ollama_cli, email_snd, exec_logs):
    """Initialize routes with dependencies"""
    global function_registry, ollama_client, email_sender, execution_logs
    function_registry = func_registry
    ollama_client = ollama_cli
    email_sender = email_snd
    execution_logs = exec_logs

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

@main_bp.route('/')
def index():
    """Main dashboard showing system status and available functions"""
    available_functions = function_registry.get_available_functions()
    return render_template('index.html', 
                         functions=available_functions,
                         recent_logs=execution_logs[-10:])

@main_bp.route('/logs')
def view_logs():
    """View execution logs"""
    return render_template('logs.html', logs=execution_logs)

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'functions_registered': len(function_registry.get_available_functions()),
        'ollama_available': ollama_client.is_available()
    })