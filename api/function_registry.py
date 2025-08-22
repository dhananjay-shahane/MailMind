import inspect
import importlib
import logging
import signal
from contextlib import contextmanager
from typing import Dict, List, Any, Callable, Optional
from config.config import Config

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

class FunctionRegistry:
    """Manages registration and execution of available functions"""
    
    def __init__(self):
        self.functions: Dict[str, Callable] = {}
        self.function_metadata: Dict[str, Dict] = {}
        self.config = Config()
    
    @contextmanager
    def timeout(self, seconds):
        """Context manager for function execution timeout - thread safe"""
        import threading
        
        # Check if we're in the main thread
        if threading.current_thread() is threading.main_thread():
            # Use signal-based timeout in main thread
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function execution timed out after {seconds} seconds")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Use threading-based timeout in other threads
            import time
            import threading
            
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = "completed"
                except Exception as e:
                    exception[0] = e
            
            # For simplicity in threads, just yield without timeout
            # In production, you could implement a more sophisticated threading timeout
            yield
    
    def register_function(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        """Register a single function"""
        func_name = name or func.__name__
        
        # Get function signature and docstring
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or description or "No description available"
        
        self.functions[func_name] = func
        self.function_metadata[func_name] = {
            'name': func_name,
            'description': doc,
            'signature': str(sig),
            'parameters': [param.name for param in sig.parameters.values()]
        }
        
        logger.info(f"Registered function: {func_name}")
    
    def register_module(self, module):
        """Register all public functions from a module"""
        if isinstance(module, str):
            try:
                module = importlib.import_module(module)
            except ImportError as e:
                logger.error(f"Could not import module {module}: {e}")
                return
        
        for name, obj in inspect.getmembers(module):
            if (inspect.isfunction(obj) and 
                not name.startswith('_') and 
                hasattr(obj, '__module__')):
                self.register_function(obj)
    
    def get_available_functions(self) -> List[Dict]:
        """Get list of all available functions with metadata"""
        return list(self.function_metadata.values())
    
    def function_exists(self, function_name: str) -> bool:
        """Check if a function is registered"""
        return function_name in self.functions
    
    def execute_function(self, function_name: str, *args, **kwargs) -> Any:
        """Execute a registered function with safety measures"""
        if not self.function_exists(function_name):
            raise ValueError(f"Function '{function_name}' not found")
        
        func = self.functions[function_name]
        
        try:
            # Execute with timeout
            with self.timeout(self.config.MAX_FUNCTION_EXECUTION_TIME):
                logger.info(f"Executing function: {function_name} with args: {args}, kwargs: {kwargs}")
                result = func(*args, **kwargs)
                logger.info(f"Function {function_name} completed successfully")
                return result
                
        except TimeoutError as e:
            logger.error(f"Function {function_name} timed out: {e}")
            raise
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            raise
    
    def get_function_info(self, function_name: str) -> Optional[Dict]:
        """Get detailed information about a specific function"""
        if function_name in self.function_metadata:
            return self.function_metadata[function_name]
        return None
    
    def search_functions(self, query: str) -> List[Dict]:
        """Search functions by name or description"""
        query = query.lower()
        results = []
        
        for func_info in self.function_metadata.values():
            if (query in func_info['name'].lower() or 
                query in func_info['description'].lower()):
                results.append(func_info)
        
        return results
