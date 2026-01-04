import re
from typing import List, Optional
from pydantic import BaseModel, Field
import html
from bs4 import BeautifulSoup
import logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


# Clean Pydantic Models
class CleanEmailData(BaseModel):
    """Pydantic model for cleaned email data."""
    email_id: str = Field(description="Unique identifier for the email.")
    from_name: Optional[str] = None
    from_email: str = Field(description="Sender's email address.")
    subject: str = Field(description="The subject of the email.")
    message: str = Field(description="The cleaned body content of the email.")
    time: str = Field(description="Human-readable timestamp of the email.")


class Emails(BaseModel):
    """Pydantic model for cleaned email response."""
    emails: List[CleanEmailData] = Field(description="List of cleaned email data.")

# Custom colored formatter
class ColoredFormatter(logging.Formatter):
    """Custom formatter with yellow color for INFO logs."""
    
    FORMATS = {
        logging.INFO: Fore.YELLOW + "%(asctime)s - [EmailPreprocessor] - INFO - %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "%(asctime)s - [EmailPreprocessor] - WARNING - %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "%(asctime)s - [EmailPreprocessor] - ERROR - %(message)s" + Style.RESET_ALL,
        logging.DEBUG: Fore.CYAN + "%(asctime)s - [EmailPreprocessor] - DEBUG - %(message)s" + Style.RESET_ALL,
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, "%(asctime)s - [EmailPreprocessor] - %(levelname)s - %(message)s")
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class EmailPreprocessor:
    """Class to preprocess and clean email data."""
    
    def __init__(self):
        """Initialize the EmailPreprocessor."""
        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Create console handler with colored formatter
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(handler)
    
    def _remove_urls(self, text: str) -> str:
        """Remove all URLs from text."""
        # Remove http/https URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[LINK REMOVED]', text)
        return text
    
    def _remove_html(self, text: str) -> str:
        """Remove HTML tags and decode HTML entities."""
        # Decode HTML entities
        text = html.unescape(text)
        
        # Use BeautifulSoup to strip HTML tags
        try:
            soup = BeautifulSoup(text, 'html.parser')
            text = soup.get_text()
        except:
            # Fallback: simple regex
            text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def _remove_special_characters(self, text: str) -> str:
        """Remove special characters and clean whitespace."""
        # Remove zero-width characters
        text = text.replace('\u200c', '')
        text = text.replace('\u200b', '')
        text = text.replace('\ufeff', '')
        
        # Replace non-breaking spaces
        text = text.replace('\xa0', ' ')
        text = text.replace('\u00a0', ' ')
        
        # Remove carriage returns and normalize newlines
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Replace multiple newlines with single newline
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' +', ' ', text)
        
        return text
    
    def _remove_email_artifacts(self, text: str) -> str:
        """Remove common email artifacts."""
        # Remove image placeholders
        text = re.sub(r'\[image:.*?\]', '', text)
        text = re.sub(r'\[cid:.*?\]', '', text)
        
        # Remove common email footers
        patterns = [
            r'You received this (?:email|message).*?(?:\n|$)',
            r'Unsubscribe.*?(?:\n|$)',
            r'Copyright \d{4}.*?(?:\n|$)',
            r'This email was sent to.*?(?:\n|$)',
            r'If you no longer wish to receive.*?(?:\n|$)',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Apply all cleaning steps to text."""
        # Step 1: Remove HTML
        text = self._remove_html(text)
        
        # Step 2: Remove URLs
        text = self._remove_urls(text)
        
        # Step 3: Remove special characters
        text = self._remove_special_characters(text)
        
        # Step 4: Remove email artifacts
        text = self._remove_email_artifacts(text)
        
        # Step 5: Final cleanup
        text = text.strip()
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text
    
    def _create_preview(self, text: str, max_length: int = 500) -> str:
        """Create a preview of the text."""
        # Get first paragraph or max_length chars
        text = text.replace('\n', ' ')
        text = ' '.join(text.split())  # Normalize spaces
        
        if len(text) > max_length:
            # Try to cut at sentence boundary
            preview = text[:max_length]
            last_period = preview.rfind('.')
            last_space = preview.rfind(' ')
            
            if last_period > max_length - 50:
                preview = preview[:last_period + 1]
            elif last_space > 0:
                preview = preview[:last_space]
            
            preview += "..."
        else:
            preview = text
        
        return preview
    
    def clean_email(self, email_data) -> CleanEmailData:
        """
        Clean a single EmailData object.
        
        Args:
            email_data: EmailData object from ReceiveEmail class
            
        Returns:
            CleanEmailData object with cleaned text
        """
        self.logger.info(f"Cleaning email: {email_data.id}")
        
        # Clean the message
        clean_message = self._clean_text(email_data.message)
        
        # Truncate message to reasonable length (500 chars)
        clean_message = self._create_preview(clean_message, max_length=500)
        
        # Create clean email object
        clean_email = CleanEmailData(
            email_id=email_data.id,
            from_name=email_data.sender_name,
            from_email=email_data.sender_email,
            subject=email_data.subject,
            message=clean_message,
            time=email_data.readable_time
        )
        
        return clean_email
    
    def process_email_response(self, email_response) -> Emails:
        """
        Process EmailResponse and return CleanEmailResponse.
        
        Args:
            email_response: EmailResponse object from ReceiveEmail class
            
        Returns:
            CleanEmailResponse with cleaned emails
        """
        try:
            if not email_response.success:
                self.logger.error(f"Email response not successful: {email_response.error}")
                return Emails(
                    emails=[]
                )
            
            self.logger.info(f"Processing {email_response.total_emails} emails")
            
            cleaned_emails = []
            for email in email_response.emails:
                cleaned_email = self.clean_email(email)
                cleaned_emails.append(cleaned_email)
            
            self.logger.info(f"Successfully cleaned {len(cleaned_emails)} emails")
            
            return Emails(
                emails=cleaned_emails
            )
            
        except Exception as e:
            self.logger.error(f"Error processing emails: {str(e)}")
            return Emails(
                emails=[]
            )


# Example usage
if __name__ == '__main__':
    # This shows how to use the preprocessor with ReceiveEmail
    from receive_email import ReceiveEmail
    
    # Step 1: Fetch emails
    receiver = ReceiveEmail()
    raw_response = receiver.fetch_unread_emails(max_results=5)
    
    # Step 2: Clean emails
    preprocessor = EmailPreprocessor()
    clean_response = preprocessor.process_email_response(raw_response)
    
    # Step 3: Use clean data

    print("=" * 70)
        
    for idx, email in enumerate(clean_response.emails, 1):
            print(f"\nEmail #{idx}")
            print(f"email_id: {email.email_id}")
            print(f"from_name: {email.from_name}")
            print(f"from_email: {email.from_email}")
            print(f"subject: {email.subject}")
            print(f"message: {email.message}")
            print(f"time: {email.time}")
            print("=" * 70)
    
    