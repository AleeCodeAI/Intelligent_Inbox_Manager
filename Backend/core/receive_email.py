import os
from xml.sax import handler
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from datetime import datetime
import re
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


# Pydantic Models
class EmailData(BaseModel):
    """Pydantic model for email data."""
    id: str
    sender_name: Optional[str] = None
    sender_email: str
    subject: str
    date: str
    timestamp: int
    readable_time: str
    message: str
    is_unread: bool = True


class EmailResponse(BaseModel):
    """Pydantic model for email fetch response."""
    success: bool
    total_emails: int
    emails: List[EmailData]
    error: Optional[str] = None

class ColoredFormatter(logging.Formatter):
    """Custom formatter with yellow color for INFO logs."""
    FORMATS = {
        logging.INFO: Fore.YELLOW + "%(asctime)s - [ReceiveEmail] - INFO - %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "%(asctime)s - [ReceiveEmail] - WARNING - %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "%(asctime)s - [ReceiveEmail] - ERROR - %(message)s" + Style.RESET_ALL,
        logging.DEBUG: Fore.CYAN + "%(asctime)s - [ReceiveEmail] - DEBUG - %(message)s" + Style.RESET_ALL,
    }
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, "%(asctime)s - [ReceiveEmail] - %(levelname)s - %(message)s")
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class ReceiveEmail:
    """Class to handle Gmail email retrieval."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
    Initialize the ReceiveEmail class.
    Args:
        credentials_path: Path to credentials.json file
        token_path: Path to token.json file
    """
    # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
    # Make paths absolute if they're relative
        if not os.path.isabs(credentials_path):
            self.credentials_path = os.path.join(script_dir, credentials_path)
        else:
            self.credentials_path = credentials_path
        
        if not os.path.isabs(token_path):
            self.token_path = os.path.join(script_dir, token_path)
        else:
            self.token_path = token_path
        self.service = None
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
    
    def authenticate(self):
        """Authenticate with Gmail API."""
        self.logger.info("Starting Gmail authentication...")
        
        creds = None
        
        if os.path.exists(self.token_path):
            self.logger.info(f"Loading existing token from {self.token_path}")
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                self.logger.info("No valid credentials found. Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            self.logger.info(f"Saving credentials to {self.token_path}")
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Authentication successful")
        return self.service
    
    def _parse_from_field(self, from_field: str) -> tuple:
        """
        Parse the 'From' field to extract name and email.
        
        Args:
            from_field: Raw 'From' header value
            
        Returns:
            Tuple of (name, email)
        """
        match = re.match(r'^(.+?)\s*<(.+?)>$', from_field)
        
        if match:
            name = match.group(1).strip()
            email = match.group(2).strip()
        else:
            name = None
            email = from_field.strip()
        
        return name, email
    
    def _get_email_body(self, payload: dict) -> str:
        """
        Extract email body from payload.
        
        Args:
            payload: Email payload from Gmail API
            
        Returns:
            Email body text
        """
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def _process_message(self, message_id: str) -> EmailData:
        """
        Process a single message and return EmailData object.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            EmailData object
        """
        msg = self.service.users().messages().get(userId='me', id=message_id).execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_field = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        
        sender_name, sender_email = self._parse_from_field(from_field)
        body = self._get_email_body(msg['payload'])
        
        timestamp_ms = int(msg['internalDate'])
        readable_time = datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
        
        return EmailData(
            id=message_id,
            sender_name=sender_name,
            sender_email=sender_email,
            subject=subject,
            date=date,
            timestamp=timestamp_ms,
            readable_time=readable_time,
            message=body,
            is_unread=True
        )
    
    def fetch_unread_emails(self, max_results: int = 50) -> EmailResponse:
        """
        Fetch unread emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            EmailResponse object with list of emails
        """
        try:
            if not self.service:
                self.authenticate()
            
            self.logger.info(f"Fetching unread emails (max: {max_results})...")
            
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX', 'UNREAD']
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                self.logger.info("No unread emails found")
                return EmailResponse(
                    success=True,
                    total_emails=0,
                    emails=[]
                )
            
            self.logger.info(f"Found {len(messages)} unread emails. Processing...")
            
            email_list = []
            for idx, message in enumerate(messages, 1):
                self.logger.info(f"Processing email {idx}/{len(messages)}")
                email_data = self._process_message(message['id'])
                email_list.append(email_data)
            
            self.logger.info(f"Successfully fetched {len(email_list)} unread emails")
            
            return EmailResponse(
                success=True,
                total_emails=len(email_list),
                emails=email_list
            )
            
        except Exception as e:
            self.logger.error(f"Failed to fetch emails: {str(e)}")
            return EmailResponse(
                success=False,
                total_emails=0,
                emails=[],
                error=str(e)
            )
    
    def fetch_all_emails(self, max_results: int = 50) -> EmailResponse:
        """
        Fetch all emails from Gmail (read and unread).
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            EmailResponse object with list of emails
        """
        try:
            if not self.service:
                self.authenticate()
            
            self.logger.info(f"Fetching all emails (max: {max_results})...")
            
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                self.logger.info("No emails found")
                return EmailResponse(
                    success=True,
                    total_emails=0,
                    emails=[]
                )
            
            self.logger.info(f"Found {len(messages)} emails. Processing...")
            
            email_list = []
            for idx, message in enumerate(messages, 1):
                self.logger.info(f"Processing email {idx}/{len(messages)}")
                email_data = self._process_message(message['id'])
                email_list.append(email_data)
            
            self.logger.info(f"Successfully fetched {len(email_list)} emails")
            
            return EmailResponse(
                success=True,
                total_emails=len(email_list),
                emails=email_list
            )
            
        except Exception as e:
            self.logger.error(f"Failed to fetch emails: {str(e)}")
            return EmailResponse(
                success=False,
                total_emails=0,
                emails=[],
                error=str(e)
            )
    


# Example usage (only for testing)
if __name__ == '__main__':
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Initialize receiver
    receiver = ReceiveEmail()
    # Fetch unread emails
    response = receiver.fetch_unread_emails(max_results=10)
    # Display results (for testing only)
    if response.success:
        print(f"Total emails: {response.total_emails}")
        for email in response.emails:
            print(f"- {email.subject} from {email.sender_email}")
    else:
        print(f"Error: {response.error}")