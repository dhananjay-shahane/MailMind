import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config.config import Config

logger = logging.getLogger(__name__)

class EmailSender:
    """Handles sending email responses"""
    
    def __init__(self):
        self.config = Config()
    
    def send_response(self, to_email: str, original_subject: str, question: str, result: str, attachment_path: str = None) -> bool:
        """Send email response with function execution result and optional chart attachment"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = f"Re: {original_subject}"
            
            # Create response body with username
            body = self._create_response_body(to_email, question, result, attachment_path)
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                
                # Add header with filename
                filename = os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}',
                )
                
                msg.attach(part)
                logger.info(f"Added chart attachment: {filename}")
            
            # Send email if SMTP is configured
            if self.config.SMTP_USERNAME and self.config.SMTP_PASSWORD:
                server = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
                if self.config.SMTP_USE_TLS:
                    server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                
                text = msg.as_string()
                server.sendmail(self.config.FROM_EMAIL, to_email, text)
                server.quit()
                
                logger.info(f"Email response sent to {to_email}")
                return True
            else:
                logger.warning("SMTP not configured, email response not sent")
                logger.info(f"Would send to {to_email}:\n{body}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email response: {e}")
            return False
    
    def _create_response_body(self, to_email: str, question: str, result: str, attachment_path: str = None) -> str:
        """Create formatted response email body with username"""
        attachment_note = ""
        if attachment_path:
            chart_name = os.path.basename(attachment_path)
            attachment_note = f"\n📊 I've attached a chart ({chart_name}) that visualizes this data for you.\n"
        
        # Extract username from email
        username = to_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        
        return f"""Hello {username},

Thank you for your question: "{question}"

Here is the result:

{result}{attachment_note}

---
This is an automated response from the Email-to-Function Execution System.
If you have any issues, please contact the system administrator.

Best regards,
Email-to-Function System
"""
    
    def send_error_notification(self, to_email: str, original_subject: str, error: str) -> bool:
        """Send error notification email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = f"Error: {original_subject}"
            
            body = f"""Hello,

We encountered an error processing your request.

Error: {error}

Please check your question and try again, or contact the system administrator.

Best regards,
Email-to-Function System
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            if self.config.SMTP_USERNAME and self.config.SMTP_PASSWORD:
                server = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
                if self.config.SMTP_USE_TLS:
                    server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                
                text = msg.as_string()
                server.sendmail(self.config.FROM_EMAIL, to_email, text)
                server.quit()
                
                logger.info(f"Error notification sent to {to_email}")
                return True
            else:
                logger.warning("SMTP not configured, error notification not sent")
                return False
                
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
