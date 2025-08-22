"""
Email integration for receiving and processing emails
"""

import os
import imaplib
import email
import logging
import time
import threading
from datetime import datetime, date
from email.header import decode_header
from config.config import Config

logger = logging.getLogger(__name__)

class EmailReceiver:
    """Handle email receiving from Gmail IMAP"""
    
    def __init__(self, function_registry, ollama_client, email_sender):
        self.config = Config()
        self.function_registry = function_registry
        self.ollama_client = ollama_client
        self.email_sender = email_sender
        self.running = False
        self.ollama_available = False
        self.last_ollama_check = 0
        
    def connect_to_gmail(self):
        """Connect to Gmail IMAP server"""
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            mail.login(self.config.EMAIL_USER, self.config.SMTP_PASSWORD)
            
            # Select inbox
            mail.select('inbox')
            logger.info("Successfully connected to Gmail IMAP")
            return mail
            
        except Exception as e:
            logger.error(f"Failed to connect to Gmail IMAP: {e}")
            return None
    
    def process_email(self, mail_data):
        """Process a single email - read content and analyze with LLM without auto-reply"""
        try:
            # Parse email
            msg = email.message_from_bytes(mail_data)
            
            # Get sender
            from_header = msg.get('From', '')
            sender_email = self.extract_email_address(from_header)
            
            # Get subject
            subject_header = msg.get('Subject', '')
            subject = self.decode_header_value(subject_header)
            
            # Get body
            body = self.extract_email_body(msg)
            
            # Skip delivery failure emails and system notifications
            if (sender_email.lower().startswith('mailer-daemon') or 
                sender_email.lower().startswith('postmaster') or 
                'delivery status notification' in subject.lower() or
                'undeliverable' in subject.lower()):
                logger.info(f"Skipping delivery failure email from {sender_email}")
                return True
                
            logger.info(f"📧 NEW EMAIL: From {sender_email} | Subject: {subject}")
            
            # Log email reception (no more websockets)
            logger.info(f"📧 Email received and being processed...")
            
            # Extract question from body
            question = self.extract_question_from_body(body)
            if not question:
                logger.info(f"Email content processed - Body preview: {body[:100]}...")
                return True
            
            # Get available functions for LLM analysis
            available_functions = self.function_registry.get_available_functions()
            
            # Check Ollama availability periodically (every 2 minutes)
            current_time = time.time()
            if current_time - self.last_ollama_check > 120:  # 2 minutes
                self.ollama_available = self.ollama_client.is_available()
                self.last_ollama_check = current_time
                if self.ollama_available:
                    logger.info(f"🤖 Ollama LLM ({self.config.OLLAMA_MODEL}) connected and ready")
                else:
                    logger.info("📴 Ollama LLM not available - using fallback analysis")
            
            # Try to identify and execute function
            function_name = None
            execution_result = None
            execution_success = False
            
            # Use Ollama or fallback analysis to identify function
            function_name = self.ollama_client.identify_function(question, available_functions)
            
            if function_name:
                logger.info(f"🎯 Function identified: {function_name}")
                
                # Execute the identified function
                try:
                    execution_result = self.function_registry.execute_function(function_name, question)
                    execution_success = True
                    logger.info(f"✅ Function executed successfully: {function_name}")
                    
                    # Log execution for monitoring
                    self.log_execution(sender_email, question, function_name, execution_result, True)
                    
                    # Check if this is a chart function and generate chart
                    chart_path = None
                    if function_name.endswith('_chart'):
                        logger.info(f"📊 Generating chart for {function_name}")
                        chart_path = execution_result  # Chart functions return the file path
                    
                    # Send email reply with results and optional chart attachment
                    reply_sent = self.email_sender.send_response(
                        sender_email, 
                        subject, 
                        question, 
                        str(execution_result) if not chart_path else f"Chart generated successfully! See attached visualization.",
                        chart_path
                    )
                    
                    if reply_sent:
                        logger.info(f"📤 Reply sent to {sender_email}")
                    else:
                        logger.info(f"📝 Reply prepared but SMTP not configured")
                        
                except Exception as e:
                    execution_success = False
                    error_msg = str(e)
                    logger.error(f"❌ Function execution failed: {error_msg}")
                    
                    # Log failed execution
                    self.log_execution(sender_email, question, function_name, None, False, error_msg)
                    
                    # Send error notification
                    self.email_sender.send_error_notification(sender_email, subject, error_msg)
                    
            else:
                logger.info("🔍 No appropriate function identified for this email")
                execution_result = "No appropriate function found for your query."
                
            # Log processing result (no more websockets)
            if execution_success and function_name:
                logger.info(f"✅ Email processed successfully: {function_name} executed")
            elif function_name:
                logger.info(f"❌ Email processing failed: {function_name} execution failed")
            else:
                logger.info(f"📝 Email analyzed but no function identified")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return False
    
    def extract_email_address(self, header_value):
        """Extract email address from header"""
        try:
            if '<' in header_value and '>' in header_value:
                return header_value.split('<')[1].split('>')[0]
            return header_value.strip()
        except:
            return header_value
    
    def decode_header_value(self, header_value):
        """Decode email header value"""
        try:
            decoded_list = decode_header(header_value)
            decoded_value = ""
            for value, encoding in decoded_list:
                if isinstance(value, bytes):
                    decoded_value += value.decode(encoding or 'utf-8')
                else:
                    decoded_value += value
            return decoded_value
        except:
            return header_value
    
    def extract_email_body(self, msg):
        """Extract text body from email message"""
        body = ""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
            else:
                if msg.get_content_type() == "text/plain":
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
            return body.strip()
        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            return ""
    
    def extract_question_from_body(self, body):
        """Extract question from email body - simple implementation"""
        # Remove common email artifacts
        lines = body.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip common email signatures and replies
            if (line.startswith('>') or 
                line.startswith('On ') or 
                'wrote:' in line or 
                line.startswith('From:') or
                line.startswith('Sent:') or
                line.startswith('To:')):
                continue
            if line:
                cleaned_lines.append(line)
        
        # Join and return first meaningful content
        if cleaned_lines:
            return ' '.join(cleaned_lines[:3])  # First 3 lines
        return body[:200] if body else None
    
    def monitor_inbox(self):
        """Monitor inbox for new emails"""
        logger.info("Starting email monitoring...")
        self.running = True
        
        while self.running:
            try:
                mail = self.connect_to_gmail()
                if not mail:
                    time.sleep(30)  # Wait 30 seconds before retrying
                    continue
                
                # Search for unseen emails from today only
                today = date.today().strftime('%d-%b-%Y')
                search_criteria = f'(UNSEEN SINCE "{today}")'
                status, messages = mail.search(None, search_criteria)
                
                if status == 'OK' and messages[0]:
                    email_ids = messages[0].split()
                    logger.info(f"Found {len(email_ids)} new emails")
                    
                    for email_id in email_ids:
                        try:
                            # Fetch email
                            status, msg_data = mail.fetch(email_id, '(RFC822)')
                            if status == 'OK':
                                # Process email
                                self.process_email(msg_data[0][1])
                                
                                # Mark as seen
                                mail.store(email_id, '+FLAGS', '\\Seen')
                                
                        except Exception as e:
                            logger.error(f"Error processing email {email_id}: {e}")
                
                mail.close()
                mail.logout()
                
                # Wait before checking again
                time.sleep(60)  # Check every 1 minute
                
            except Exception as e:
                logger.error(f"Error in email monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def start_monitoring(self):
        """Start email monitoring in a separate thread"""
        if not self.running:
            monitor_thread = threading.Thread(target=self.monitor_inbox, daemon=True)
            monitor_thread.start()
            logger.info("Email monitoring thread started")
    
    def stop_monitoring(self):
        """Stop email monitoring"""
        self.running = False
        logger.info("Email monitoring stopped")
    
    def log_execution(self, email_from, question, function_name, result, success=True, error=None):
        """Log function execution for monitoring"""
        try:
            # Import the execution_logs from main module
            import main
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'email_from': email_from,
                'question': question,
                'function_name': function_name,
                'result': str(result)[:500] if result else None,
                'success': success,
                'error': str(error) if error else None
            }
            main.execution_logs.append(log_entry)
            
            # Keep only last 100 logs
            if len(main.execution_logs) > 100:
                main.execution_logs.pop(0)
                
        except Exception as e:
            # Silently fail if logging fails
            logger.debug(f"Failed to log execution: {e}")