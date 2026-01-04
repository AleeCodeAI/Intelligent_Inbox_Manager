from agents.scheduler_agent.read_calendar import read_calendar_events
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import os 
from dotenv import load_dotenv
from openai import OpenAI
from agents.scheduler_agent.send_email import send_to_n8n
import sqlite3
import logging
from Backend.color import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

load_dotenv(override=True)
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")

class CleanEmailData(BaseModel):
    """Pydantic model for cleaned email data."""
    email_id: str = Field(description="Unique identifier for the email.")
    from_name: Optional[str] = None
    from_email: str = Field(description="Sender's email address.")
    subject: str = Field(description="The subject of the email.")
    message: str = Field(description="The cleaned body content of the email.")
    time: str = Field(description="Human-readable timestamp of the email.")

class Email(BaseModel):
    body: str = Field(description="The raw body content of the email.")

SYSTEM_PROMPT = """
You are a Scheduler Agent that proposes appointment availability via email on behalf of Alee, an Applied AI Engineer.

You receive:
- Calendar events with date (YYYY-MM-DD), start_time, and end_time.
- Recipient name and email.
- Today's date.
- (Optional) The recipient's requested or expected appointment time.

Your job is to find the SINGLE earliest valid appointment slot and propose it via email.
It is MANDATORY to always propose an appointment if you are invoked. Even if the recipient 
does not explicitly request an appointment, if the message implies a discussion would be 
beneficial, you must schedule the earliest available time.

RULES (STRICT):

1. Allowed appointment windows ONLY:
   - 08:00–10:00
   - 21:00–23:00

2. Allowed dates:
   - Appointments can be scheduled starting from TOMORROW ONLY.
   - Appointments may be scheduled on any day within the following month.
   - You must clearly emphasize that appointments cannot be scheduled earlier than tomorrow.

3. Availability:
   - A window is unavailable if any event overlaps it
     (event_start < window_end AND event_end > window_start).
   - Skip dates where both windows are unavailable.

4. Slot selection (CRITICAL):
   - Choose ONLY ONE slot.
   - It must be the earliest upcoming valid slot.
   - NEVER list multiple dates or times.
   - NEVER offer alternatives or options.

5. Recipient expectation handling:
   - If the recipient expects or requests a time that is unavailable or invalid,
     you must briefly apologize.
   - After apologizing, propose the nearest EARLIER valid available slot
     (never a later one).
   - Do not mention unavailability details or internal reasoning.

6. Email writing:
   - Propose the selected date and time clearly.
   - Ask for confirmation of that exact slot.
   - Be polite and professional.
   - Do not mention rules or analysis.
   - End the email by mentioning ONLY:
     - Sender name: Alee
     - Position: Applied AI Engineer

7. HTML Formatting (REQUIRED):
   - Write the ENTIRE email in well-formatted HTML.
   - Use a clean, professional design with proper styling.
   - Highlight the appointment date and time prominently using a styled box or card.
   - Use appropriate colors: subtle backgrounds, professional text colors.
   - Ensure the email is responsive and looks good on all devices.
   - Include proper spacing and typography.

8. No availability:
   - If no valid slot exists, send a polite HTML-formatted email stating that no appointments
     can be scheduled at this time and availability will be shared later.

Any output containing multiple appointment options or flexible wording is INVALID.

EXAMPLE HTML EMAIL FORMAT:

<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { margin-bottom: 20px; }
        .appointment-box { 
            background: #f0f8ff; 
            border-left: 4px solid #4a90e2; 
            padding: 15px; 
            margin: 20px 0; 
            border-radius: 5px; 
        }
        .date { font-size: 18px; font-weight: bold; color: #4a90e2; }
        .time { font-size: 16px; color: #555; margin-top: 5px; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }
        .signature { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <p>Dear [Recipient Name],</p>
        </div>
        
        <p>[Your message content here]</p>
        
        <div class="appointment-box">
            <div class="date">📅 January 15, 2026</div>
            <div class="time">🕐 08:00 AM - 10:00 AM</div>
        </div>
        
        <p>[Request for confirmation]</p>
        
        <div class="footer">
            <p>Best regards,</p>
            <div class="signature">
                <strong>Alee</strong><br>
                Applied AI Engineer
            </div>
        </div>
    </div>
</body>
</html>

Follow this structure and styling approach for all emails you generate.
"""

USER_PROMPT = """ 
Here are the lists of calendar events:
{calendar_events}

Here are the recipient details:

Recipient Name: {from_name}
Recipient Email: {from_email}
Today's Date: {today_date}
Recipient's Email Content:
{message}

now please draft an email proposing appointment availability based on the rules.
"""

class SchedulerAgent(Agent):
    name = "SchedulerAgent"
    color = Agent.BLUE
    
    def __init__(self):
        self.client = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)
        self.system_prompt = SYSTEM_PROMPT
        self.user_prompt = USER_PROMPT
        self.response_format = Email
        self.send_email = send_to_n8n
        self.log("Initialized SchedulerAgent")

    def insert_email(self, email: CleanEmailData):
        """Insert email into the database."""
        DB_FOLDER = r"D:\Projects\inbox-manager\databases"
        DB_NAME = os.path.join(DB_FOLDER, "scheduler_emails.db")
        os.makedirs(DB_FOLDER, exist_ok=True)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            email_id TEXT PRIMARY KEY,
            from_name TEXT,
            from_email TEXT NOT NULL,
            subject TEXT,
            message TEXT,
            time TEXT
        )""")
        cursor.execute("""
        INSERT OR REPLACE INTO emails
        (email_id, from_name, from_email, subject, message, time)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
        email.email_id,
        email.from_name,
        email.from_email,
        email.subject,
        email.message,
        email.time))
        conn.commit()
        conn.close()
        self.log(f"Email {email.email_id} inserted into database")

    def get_events(self):
        self.log("Fetching calendar events")
        events = read_calendar_events()
        self.log(f"Retrieved {len(events) if isinstance(events, list) else 'calendar'} events")
        return events

    def make_messages(self, email, events):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt.format(
                calendar_events=events,
                from_name=email.from_name,
                from_email=email.from_email,
                today_date=date.today(),
                message=email.message
            )},
        ]
        return messages
    
    def generate_email(self, email: CleanEmailData) -> Email:
        self.log(f"Generating appointment email for {email.from_email}")
        events = self.get_events()
        response = self.client.chat.completions.parse(
            model="gpt-oss-120b",
            messages=self.make_messages(email, events),
            response_format=self.response_format
        )
        parsed_email = response.choices[0].message.parsed
        result = self.send_email({
            "id": email.email_id,
            "body": parsed_email.body
        })
        self.log(f"EMAIL STATUS: {result['status']}, EMAIL ID: {result['emailId']}")
        return parsed_email

    def run(self, email: CleanEmailData) -> Email:
        self.log(f"Processing scheduler request from {email.from_email}")
        
        # First attempt
        try:
            self.log("Attempt 1: Generating email")
            email_response = self.generate_email(email)
            self.log(f"Successfully processed scheduler request for {email.email_id} on first attempt")
            return email_response
        except Exception as e:
            self.log(f"Attempt 1 failed: {str(e)}")
            
            # Second attempt
            try:
                self.log("Attempt 2: Retrying email generation")
                email_response = self.generate_email(email)
                self.log(f"Successfully processed scheduler request for {email.email_id} on second attempt")
                return email_response
            except Exception as e2:
                self.log(f"Attempt 2 failed: {str(e2)}")
                self.log(f"Both attempts failed, saving to database")
                self.insert_email(email)
                return Email(body="An error occurred while generating the email after 2 attempts. The email has been saved to the database.")

if __name__ == "__main__":

    email = CleanEmailData(
    email_id="19b640e16056d87c",
    from_name="Sarah Johnson",
    from_email="aleeghulami2024@gmail.com",
    subject="Request for Appointment Availability",
    message=(
        "Hello,\n\n"
        "I hope you are doing well.\n\n"
        "I wanted to ask if you would be available for an appointment today"
        "Please let me know what time works best for you.\n\n"
        "Looking forward to your response.\n\n"
        "Best regards,\n"
        "Sarah Johnson"
    ),
    time="December 30, 2025, 9:15 AM"
)
    agent = SchedulerAgent()
    generated_email = agent.run(email)
    agent.log(f"Generated Email Body:\n{generated_email.body}")