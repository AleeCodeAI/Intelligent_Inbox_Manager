import requests 
from utils.color import Logger
import logging
from configs import MainSettings
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO, format="%(message)s")

class SendExampleEmails(Logger):
    name: str = "SendExampleEmails"
    color: str = Logger.ORANGE
    
    def __init__(self):
        self.settings = MainSettings()
        self.url = self.settings.SEND_EXAMPLE_EMAILS_N8N_URL
        self.basic_emails_path = Path(__file__).parent / "basic_emails.jsonl"
        self.priority_emails_path = Path(__file__).parent / "priority_emails.jsonl"
        self.nonbusiness_emails_path = Path(__file__).parent / "nonbusiness_emails.jsonl"
        self.log("Initialized SendExampleEmails")

    def load_basic_emails(self):
        basic_emails = []

        with open(self.basic_emails_path, "r") as file:
            for line in file:
                basic_emails.append(json.loads(line))

        return basic_emails[23:25]
    
    def load_priority_emails(self):
        priority_emails = []

        with open(self.priority_emails_path, "r") as file:
            for line in file:
                priority_emails.append(json.loads(line))

        return priority_emails[7:8]

    def load_nonbusiness_emails(self):
        nonbusiness_emails = []

        with open(self.nonbusiness_emails_path, "r") as file:
            for line in file:
                nonbusiness_emails.append(json.loads(line))

        return nonbusiness_emails[5:6]
    
    def load_all_emails(self):
        all_emails = []

        all_emails.extend(self.load_basic_emails())
        all_emails.extend(self.load_priority_emails())
        all_emails.extend(self.load_nonbusiness_emails())

        return all_emails

    def send_email(self, email: InboundEmail):
        # model_dump(mode="json") serializes everything, including datetimes, into JSON-compatible primitives
        payload = {"email": email.model_dump(mode="json")}
        
        try:
            response = requests.post(self.url, json=payload)
            if response.status_code == 200:
                self.log(f"Email sent successfully to {email.subject}")
            else:
                self.log(f"Failed to send email to {email.subject}. Status code: {response.status_code}")
            return response
        except Exception as e:
            self.log(f"An error occurred while sending email to {email.subject}: {str(e)}")
            return None

if __name__ == "__main__":
    from schemas import InboundEmail

    sender = SendExampleEmails()

    emails = sender.load_all_emails()

    for email_data in emails:

        email = InboundEmail(**email_data)

        sender.send_email(email)