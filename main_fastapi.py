import os
import logging
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import threading

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

# Create FastAPI app
app = FastAPI(title="Email-to-Function Execution System", version="1.0.0")

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
        'result': str(result)[:500] if result else None,
        'success': success,
        'error': str(error) if error else None
    }
    execution_logs.append(log_entry)
    # Keep only last 100 logs
    if len(execution_logs) > 100:
        execution_logs.pop(0)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard showing system status and available functions"""
    available_functions = function_registry.get_available_functions()
    return templates.TemplateResponse("index_fastapi.html", {
        "request": request,
        "functions": available_functions,
        "recent_logs": execution_logs[-10:]
    })

@app.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request):
    """View execution logs"""
    return templates.TemplateResponse("logs_fastapi.html", {
        "request": request,
        "logs": execution_logs
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'functions_registered': len(function_registry.get_available_functions()),
        'ollama_available': ollama_client.is_available(),
        'total_logs': len(execution_logs)
    }

@app.get("/api/functions")
async def get_functions():
    """Get available functions via API"""
    return function_registry.get_available_functions()

@app.post("/api/execute")
async def execute_function(request: Request):
    """Execute a function via API"""
    data = await request.json()
    function_name = data.get('function_name')
    question = data.get('question', '')
    
    if not function_name:
        raise HTTPException(status_code=400, detail="function_name is required")
    
    try:
        result = function_registry.execute_function(function_name, question)
        log_execution("api", question, function_name, result, True)
        return {"success": True, "result": result}
    except Exception as e:
        log_execution("api", question, function_name, None, False, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/email")
async def email_webhook(request: Request):
    """Webhook endpoint for processing emails"""
    try:
        data = await request.json()
        
        # Process email
        email_data = email_processor.parse_email(data.get('raw_email', ''))
        if not email_data:
            raise HTTPException(status_code=400, detail="Invalid email data")
        
        question = email_processor.extract_question(email_data['body'])
        if not question:
            return {"message": "No question found in email"}
        
        # Get available functions
        available_functions = function_registry.get_available_functions()
        
        # Use Ollama to identify function
        function_name = ollama_client.identify_function(question, available_functions)
        if not function_name:
            return {"message": "No appropriate function identified"}
        
        # Execute function
        result = function_registry.execute_function(function_name, question)
        
        # Log execution
        log_execution(email_data['from'], question, function_name, result, True)
        
        return {
            "success": True, 
            "function_executed": function_name,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing email webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize and start email receiver
email_receiver = None

@app.on_event("startup")
async def startup_event():
    """Initialize email monitoring on startup"""
    global email_receiver
    try:
        email_receiver = EmailReceiver(function_registry, ollama_client, email_sender)
        # Start email monitoring in a separate thread
        monitor_thread = threading.Thread(target=email_receiver.start_monitoring, daemon=True)
        monitor_thread.start()
        logger.info("Email receiver started successfully")
    except Exception as e:
        logger.error(f"Failed to start email receiver: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global email_receiver
    if email_receiver:
        email_receiver.stop_monitoring()
        logger.info("Email monitoring stopped")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Email-to-Function Execution System with FastAPI")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=False)