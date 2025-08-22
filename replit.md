# Email-to-Function Execution System

## Overview

This is an email-to-function execution system built with Flask that allows users to execute registered functions by sending natural language emails. The system processes incoming emails, extracts questions or requests, uses an AI model (Ollama) to map those requests to appropriate functions, executes the functions, and sends back email responses with the results. It features a web dashboard for monitoring executions, viewing logs, and managing the system.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask-based architecture** with a modular component design
- **Template rendering** using Jinja2 for the web dashboard interface
- **Static file serving** for CSS and client-side assets
- **RESTful API endpoints** for webhook processing and system health checks

### Core Components
- **EmailProcessor**: Handles parsing of raw email content and question extraction using Python's email.parser
- **FunctionRegistry**: Manages function registration, metadata storage, and secure execution with timeout controls
- **OllamaClient**: Interfaces with the Ollama LLM service for natural language processing and function mapping
- **EmailSender**: Handles SMTP-based email response delivery with proper formatting

### Function Execution System
- **Dynamic function registration** from Python modules with automatic signature detection
- **Timeout protection** using signal handlers to prevent runaway executions
- **Execution logging** with truncated results and error handling for monitoring
- **Sample functions** demonstrating sales calculations, user counts, and weather data

### Security and Safety
- **Module whitelisting** through ALLOWED_MODULES configuration
- **Function execution timeouts** with configurable limits
- **Input sanitization** for email content processing
- **Error isolation** to prevent function failures from crashing the system

### Configuration Management
- **Environment-based configuration** for all external service connections
- **Centralized Config class** managing Ollama, SMTP, and security settings
- **Development defaults** with production-ready override capabilities

### Monitoring and Observability
- **Execution logging** with timestamp tracking and result storage
- **Web dashboard** showing system status, function registry, and recent executions
- **Health check endpoints** for service monitoring
- **Log management** with automatic rotation and manual clearing capabilities

## External Dependencies

### AI/LLM Services
- **Ollama**: Local LLM service for natural language processing and function mapping
  - Configurable model selection (default: llama2)
  - Health checking and availability detection
  - Timeout handling for API calls

### Email Services
- **SMTP servers**: For sending email responses (Gmail SMTP as default)
  - Configurable host, port, and authentication
  - Support for TLS/STARTTLS encryption
  - Graceful degradation when SMTP is not configured

### Frontend Libraries
- **Bootstrap**: UI framework with dark theme support
- **Feather Icons**: Icon library for the web interface
- **Replit Bootstrap Theme**: Custom dark theme for consistent styling

### Python Libraries
- **Flask**: Web framework and templating
- **Requests**: HTTP client for Ollama API communication
- **Email libraries**: Built-in Python email parsing and MIME handling
- **Signal handling**: For function execution timeout management