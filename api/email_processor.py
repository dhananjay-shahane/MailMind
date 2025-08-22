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
        """Extract the main question from email body with improved content detection"""
        if not email_body:
            logger.warning("Empty email body provided")
            return None
            
        # Clean up the email body more aggressively
        lines = email_body.strip().split('\n')
        cleaned_lines = []
        
        # Skip email headers, signatures, and other artifacts
        skip_patterns = [
            r'^>.*',  # Quoted text
            r'^On .* wrote:.*',  # Reply headers
            r'^From:.*', r'^To:.*', r'^Subject:.*', r'^Date:.*',  # Email headers
            r'.*sent from.*', r'.*sent via.*',  # Mobile signatures
            r'^--.*', r'^___.*',  # Signature separators
            r'^\s*$',  # Empty lines
            r'.*unsubscribe.*', r'.*click here.*', r'.*privacy policy.*',  # Marketing content
            r'.*view in browser.*', r'.*if you cannot read.*'  # HTML email artifacts
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line should be skipped
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if not should_skip and len(line) > 3:  # Minimum meaningful length
                cleaned_lines.append(line)
        
        if not cleaned_lines:
            logger.warning("No meaningful content found in email after cleaning")
            return None
        
        # Join lines and clean up the text
        text = ' '.join(cleaned_lines)
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.info(f"📧 Cleaned email content: '{text[:150]}...'")
        
        # Look for explicit questions first (highest priority)
        question_patterns = [
            r'[^.!]*\?[^.!]*',  # Text ending with question mark
            r'(?:what|how|when|where|why|which|who).*?(?:[.!?]|$)',  # Wh-questions
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                question = matches[0].strip()
                if len(question) > 5:  # Meaningful question
                    logger.info(f"🔍 Found explicit question: '{question}'")
                    return question
        
        # Look for imperative requests and statements
        request_patterns = [
            r'(?:please\s+)?(?:can you\s+|could you\s+|would you\s+)?(?:show me\s+|tell me\s+|get me\s+|give me\s+|find\s+|calculate\s+|generate\s+|create\s+)(.+?)(?:[.!?]|$)',
            r'(?:i need\s+|i want\s+|i would like\s+|i\'d like\s+)(.+?)(?:[.!?]|$)',
            r'(?:what is\s+|what are\s+|how much\s+|how many\s+|show me\s+)(.+?)(?:[.!?]|$)',
            r'(?:get\s+|show\s+|display\s+|provide\s+)(?:the\s+|my\s+)?(.+?)(?:[.!?]|$)'
        ]
        
        for pattern in request_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                request = match.group(0).strip()
                if len(request) > 8:  # Meaningful request
                    logger.info(f"🔍 Found request pattern: '{request}'")
                    return request
        
        # Look for business-related keywords that indicate intent
        business_keywords = [
            'users?', 'customers?', 'sales?', 'revenue', 'analytics?', 'metrics?', 
            'traffic', 'conversion', 'growth', 'products?', 'chart', 'graph', 
            'report', 'data', 'statistics?', 'numbers?', 'breakdown', 'total'
        ]
        
        keyword_pattern = r'.*(?:' + '|'.join(business_keywords) + r').*'
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and re.search(keyword_pattern, sentence, re.IGNORECASE):
                logger.info(f"🔍 Found business-related sentence: '{sentence}'")
                return sentence
        
        # Fallback: return the longest meaningful sentence
        longest_sentence = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > len(longest_sentence) and len(sentence) > 15:
                longest_sentence = sentence
        
        if longest_sentence:
            logger.info(f"🔍 Using longest sentence: '{longest_sentence}'")
            return longest_sentence
        
        # Final fallback: return truncated text if nothing else works
        if len(text) > 10:
            logger.warning(f"🔍 Using truncated text as fallback: '{text[:100]}'")
            return text[:100] + "..." if len(text) > 100 else text
        
        logger.warning("No meaningful question or request found in email")
        return None
    
    def is_valid_email_format(self, email_data):
        """Validate email data format"""
        required_fields = ['from', 'body']
        return all(field in email_data and email_data[field] for field in required_fields)
