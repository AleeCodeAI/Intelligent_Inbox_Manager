import requests
from schemas import InboundEmailBatch
from configs import MainSettings
from utils.color import Logger
from core.email_preprocessor import EmailPreprocessor
import logging


logging.basicConfig(level=logging.INFO, format="%(message)s")

class EmailReceiver(Logger):
    name: str = "EmailReceiver"
    color: str = Logger.BLUE

    def __init__(self):
        settings = MainSettings()
        self.url = settings.N8N_GET_EMAILS_WEBHOOK_URL
        self.preprocessor = EmailPreprocessor()
        self.log("Initialized EmailReceiver with n8n webhook URL")

    def get_emails(self) -> InboundEmailBatch:
        """
        Call the n8n webhook to fetch new unread emails.
        
        Returns:
            InboundEmailBatch with structured list of emails.
            
        Raises:
            requests.HTTPError: On non-2xx response from n8n.
            requests.ConnectionError: If n8n is unreachable.
            requests.Timeout: If the request exceeds timeout.
            ValueError: If response cannot be parsed into expected schema.
        """

        self.log("Fetching new emails from n8n...")

        try:
            response = requests.get(self.url, timeout=200)
            response.raise_for_status()
        except requests.Timeout:
            self.log("Request to n8n timed out")
            raise
        except requests.ConnectionError:
            self.log("Could not connect to n8n — is it running?")
            raise
        except requests.HTTPError as e:
            self.log(f"n8n returned an error: {e.response.status_code}")
            raise

        try:
            data = response.json()
            result = InboundEmailBatch(**data)
            self.log(f"Successfully parsed n8n response with {result.total} emails")

        except Exception as e:
            self.log(f"Failed to parse n8n response: {e}")
            raise ValueError(f"Unexpected response shape from n8n: {e}") from e

        self.log("Preprocessing email bodies...")
        for email in result.emails:
            email.body = self.preprocessor.clean(email.body)

        self.log(f"Fetched {result.total} new emails")
        return result


if __name__ == "__main__":
    receiver = EmailReceiver()
    try:
        emails = receiver.get_emails()

        print("\n" + "="*60)
        print(f"TOTAL EMAILS: {emails.total}")
        print("="*60)

        for i, email in enumerate(emails.emails, 1):
            print(f"\n📧 EMAIL #{i}")
            print("-"*60)
            print(f"ID           : {email.gmail_id}")
            print(f"Thread ID    : {email.thread_id}")
            print(f"Sender       : {email.sender_name} <{email.sender_email}>")
            print(f"Subject      : {email.subject}")
            print(f"Date         : {email.date}")
            print("\nBODY:")
            print(email.body)
            print("-"*60)

        print("\n" + "="*60)

    except Exception as e:
        print(f"Error fetching emails: {e}")