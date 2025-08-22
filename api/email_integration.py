"""
Email integration for receiving and processing emails
"""

import os
import imaplib
import email
import logging
import time
import threading
from datetime import datetime
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
            
            logger.info(f"New email received from {sender_email} with subject: {subject}")
            
            # Extract question from body
            question = self.extract_question_from_body(body)
            if not question:
                logger.info(f"Email content processed - Body preview: {body[:100]}...")
                return True
            
            # Get available functions for LLM analysis
            available_functions = self.function_registry.get_available_functions()
            
            # Use Ollama to analyze content (but don't execute automatically)
            function_name = self.ollama_client.identify_function(question, available_functions)
            if function_name:
                logger.info(f"LLM analyzed content and identified potential function: {function_name}")
            else:
                logger.info("LLM analyzed content - no specific function identified")
            
            # Log the email content for review (without auto-execution or auto-reply)
            logger.info(f"Email content analyzed: {question[:200]}...")
            
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
                
                # Search for unseen emails
                status, messages = mail.search(None, 'UNSEEN')
                
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
                time.sleep(30)  # Check every 30 seconds
                
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