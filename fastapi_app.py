import os
import logging
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import json

from email_processor import EmailProcessor
from function_registry import FunctionRegistry
from ollama_client import OllamaClient
from email_sender import EmailSender

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Email-to-Function Execution System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard showing system status and available functions"""
    available_functions = function_registry.get_available_functions()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "functions": available_functions,
        "recent_logs": execution_logs[-10:]
    })

@app.post("/webhook/email")
async def email_webhook(request: Request):
    """
    Webhook endpoint to receive email content
    Expected format: JSON with 'from', 'subject', 'body' fields
    """
    try:
        # Log the incoming request
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Received webhook request from {client_host}")
        
        # Get JSON data from request
        data = await request.json()
        if not data:
            logger.error("No JSON data received")
            raise HTTPException(status_code=400, detail="No JSON data provided")
            
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
            raise HTTPException(status_code=400, detail=error_msg)
            
        logger.info(f"Extracted question: {question}")
        
        # Get available functions for context
        available_functions = function_registry.get_available_functions()
        
        # Use Ollama to determine which function to call
        function_name = ollama_client.identify_function(question, available_functions)
        if not function_name:
            error_msg = "Could not identify appropriate function for the question"
            logger.warning(error_msg)
            log_execution(email_from, question, None, None, False, error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
            
        logger.info(f"Identified function: {function_name}")
        
        # Execute the function
        try:
            result = function_registry.execute_function(function_name, question)
            logger.info(f"Function execution successful: {result}")
            
            # Send email response
            response_sent = email_sender.send_response(email_from, email_subject, question, result)
            
            # Log successful execution
            log_execution(email_from, question, function_name, result, True)
            
            return JSONResponse({
                "success": True,
                "function_executed": function_name,
                "result": result,
                "email_sent": response_sent
            })
            
        except Exception as func_error:
            error_msg = f"Error executing function {function_name}: {str(func_error)}"
            logger.error(error_msg)
            log_execution(email_from, question, function_name, None, False, func_error)
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/test", response_class=HTMLResponse)
async def test_function_get(request: Request):
    """Test endpoint GET to display test form"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "functions": function_registry.get_available_functions(),
        "recent_logs": execution_logs[-10:],
        "show_test": True
    })

@app.post("/test", response_class=HTMLResponse)
async def test_function_post(request: Request, question: str = Form(...)):
    """Test endpoint POST to manually test function execution"""
    try:
        if not question.strip():
            return templates.TemplateResponse("index.html", {
                "request": request,
                "functions": function_registry.get_available_functions(),
                "recent_logs": execution_logs[-10:],
                "show_test": True,
                "error": "Please enter a question"
            })
            
        # Get available functions
        available_functions = function_registry.get_available_functions()
        
        # Use Ollama to identify function
        function_name = ollama_client.identify_function(question, available_functions)
        if not function_name:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "functions": function_registry.get_available_functions(),
                "recent_logs": execution_logs[-10:],
                "show_test": True,
                "error": "Could not identify appropriate function for the question"
            })
            
        # Execute function
        result = function_registry.execute_function(function_name, question)
        
        # Log execution
        log_execution('test@system.local', question, function_name, result, True)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "functions": function_registry.get_available_functions(),
            "recent_logs": execution_logs[-10:],
            "show_test": True,
            "success": f'Function "{function_name}" executed successfully!',
            "result": result
        })
        
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "functions": function_registry.get_available_functions(),
            "recent_logs": execution_logs[-10:],
            "show_test": True,
            "error": f"Error: {str(e)}"
        })

@app.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request):
    """View execution logs"""
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": execution_logs
    })

@app.get("/api/functions")
async def api_functions():
    """API endpoint to get available functions"""
    return JSONResponse(function_registry.get_available_functions())

@app.get("/api/logs")
async def api_logs():
    """API endpoint to get execution logs"""
    return JSONResponse(execution_logs)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "functions_registered": len(function_registry.get_available_functions()),
        "ollama_available": ollama_client.is_available()
    })

# Email processing endpoint specifically for dhanushahane01@gmail.com
@app.post("/process-email/dhanushahane01@gmail.com")
async def process_dhanush_email(request: Request):
    """
    Special endpoint for processing emails sent to dhanushahane01@gmail.com
    This simulates receiving an email to that specific address
    """
    try:
        data = await request.json()
        
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
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get available functions and identify the right function
        available_functions = function_registry.get_available_functions()
        function_name = ollama_client.identify_function(question, available_functions)
        
        if not function_name:
            error_msg = "Could not identify appropriate function for the question"
            logger.warning(error_msg)
            log_execution(email_from, question, None, None, False, error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Execute the identified function
        result = function_registry.execute_function(function_name, question)
        logger.info(f"Function {function_name} executed successfully: {result}")
        
        # Send email response back to the sender
        response_sent = email_sender.send_response(email_from, email_subject, question, result)
        
        # Log the execution
        log_execution(email_from, question, function_name, result, True)
        
        return JSONResponse({
            "success": True,
            "target_email": target_email,
            "from_email": email_from,
            "function_executed": function_name,
            "result": result,
            "email_response_sent": response_sent
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing email for {target_email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Email-to-Function Execution System with FastAPI")
    uvicorn.run(app, host="0.0.0.0", port=5000)