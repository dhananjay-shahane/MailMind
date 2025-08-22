import re
import logging
from email.parser import Parser
from email.policy import default

logger = logging.getLogger(__name__)

class EmailProcessor:
    """Handles email parsing and question extraction"""
    
    def __init__(self):
        self.parser = Parser(policy=default)
    
    def parse_email(self, raw_email):
        """Parse raw email content"""
        try:
            message = self.parser.parsestr(raw_email)
            return {
                'from': message.get('From', ''),
                'to': message.get('To', ''),
                'subject': message.get('Subject', ''),
                'body': self._get_email_body(message)
            }
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None
    
    def _get_email_body(self, message):
        """Extract email body from message object"""
        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_content()
        else:
            if message.get_content_type() == "text/plain":
                body = message.get_content()
        return body.strip()
    
    def extract_question(self, email_body):
        """Extract the main question from email body"""
        if not email_body:
            return None
            
        # Clean up the email body
        lines = email_body.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip common email artifacts
            if line.startswith('>') or line.startswith('On ') or line.startswith('From:'):
                continue
            if 'wrote:' in line or 'sent from' in line.lower():
                continue
            if line:
                cleaned_lines.append(line)
        
        if not cleaned_lines:
            return None
            
        # Join lines and look for question patterns
        text = ' '.join(cleaned_lines)
        
        # Look for explicit questions (containing question marks)
        question_sentences = re.findall(r'[^.!?]*\?[^.!?]*', text)
        if question_sentences:
            # Return the first question found
            return question_sentences[0].strip()
        
        # If no explicit questions, look for imperative statements or requests
        request_patterns = [
            r'(?:please\s+)?(?:can you\s+)?(?:could you\s+)?(?:show me\s+)?(?:tell me\s+)?(?:get me\s+)?(?:find\s+)?(?:calculate\s+)?(.+)',
            r'(?:i need\s+)?(?:i want\s+)?(?:i would like\s+)?(.+)',
            r'(?:what is\s+)?(?:what are\s+)?(?:how much\s+)?(?:how many\s+)?(.+)'
        ]
        
        for pattern in request_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        # If all else fails, return the first meaningful sentence
        sentences = re.split(r'[.!]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Meaningful length
                return sentence
        
        return text[:200] if text else None  # Fallback to truncated text
    
    def is_valid_email_format(self, email_data):
        """Validate email data format"""
        required_fields = ['from', 'body']
        return all(field in email_data and email_data[field] for field in required_fields)
