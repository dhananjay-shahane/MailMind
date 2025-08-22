import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

logger = logging.getLogger(__name__)

class EmailSender:
    """Handles sending email responses"""
    
    def __init__(self):
        self.config = Config()
    
    def send_response(self, to_email: str, original_subject: str, question: str, result: str) -> bool:
        """Send email response with function execution result"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = f"Re: {original_subject}"
            
            # Create response body
            body = self._create_response_body(question, result)
            msg.attach(MIMEText(body, 'plain'))
            
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
    
    def _create_response_body(self, question: str, result: str) -> str:
        """Create formatted response email body"""
        return f"""Hello,

Thank you for your question: "{question}"

Here is the result:

{result}

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
