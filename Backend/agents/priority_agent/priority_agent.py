import sqlite3
import os
import re
from pydantic import BaseModel, Field
from typing import Optional
from Backend.color import Agent
import logging 
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------------------------------

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

class Classification(BaseModel):
    classification: str = Field(description="the type of priority email: APPOINTMENT | CLIENT_COMMUNICATION | HIGH_VALUE |SENSITIVE")
    confidence: float = Field(description="confidence level for certain classification: 0.0 - 1.0")
    reasoning: str = Field(description="short explanation of why certain classification is made.")

class Priority(BaseModel):
    email_id: str = Field(description="Unique identifier for the email.")
    from_name: Optional[str] = None
    from_email: str = Field(description="Sender's email address.")
    subject: str = Field(description="The subject of the email.")
    message: str = Field(description="The cleaned body content of the email.")
    time: str = Field(description="Human-readable timestamp of the email.")
    classification: str = Field(description="the type of priority email: APPOINTMENT | CLIENT_COMMUNICATION | HIGH_VALUE | SENSITIVE")
    confidence: float = Field(description="confidence level for certain classification: 0.0 - 1.0")
    reasoning: str = Field(description="short explanation of why certain classification is made.")

SYSTEM_PROMPT = """ 
You are a Priority Email Classification Assistant. Your task is to read any given email and classify it into **exactly one** of the following categories based on its content, sender, and purpose:

1. Appointment – Emails related to appointment confirmations, acceptances, or scheduling.  
2. Client Communication – Emails that are part of ongoing communications with current clients.  
3. High-Value Project Inquiry – Emails inquiring about projects or services valued at $5,000 or more.  
4. Sensitive – Emails involving legal, financial, contractual, or compliance issues, including bank notifications.

Your classification must be **based on the content and context of the email**, and you must choose **only one category** per email. Do not provide multiple options.  

After classifying the email, return a JSON object in the following format:  

{
  "classification": "<one of APPOINTMENT, CLIENT_COMMUNICATION, HIGH_VALUE, SENSITIVE",
  "confidence": <a float between 0.0 and 1.0 representing your confidence>,
  "reasoning": "<a concise explanation of why this classification was chosen based on the email content>"
}

The reasoning should clearly refer to the content, sender, context, or urgency of the email. The confidence should reflect how certain you are about the classification.  

Do not include any text outside the JSON. Always follow these instructions strictly.

"""

class PriorityAgent(Agent):
    name = "PriorityAgent"
    color = Agent.YELLOW
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.client = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)
        self.model = os.getenv("DEEPSEEK_MODEL")

    def user(self, email: CleanEmailData) -> str:
        """Format email data for classification."""
        return f"""
Subject: {email.subject}
From: {email.from_name or 'Unknown'} <{email.from_email}>
Time: {email.time}

Message:
{email.message}
"""

    def classifier(self, email: CleanEmailData) -> Classification:
        """Classify the email using AI."""
        self.log(f"Starting priority classification for email_id={email.email_id}")
        self.log(f"Email subject: '{email.subject}' from {email.from_email}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": self.user(email)},
                ],
                temperature=0.3
            )
    
            # Get the response content
            content = response.choices[0].message.content
            
            # Clean the response by removing markdown code blocks
            cleaned_content = re.sub(r'```json\s*|\s*```', '', content).strip()
            
            # Parse with Pydantic
            result = Classification.model_validate_json(cleaned_content)
            
            self.log(f"Classification complete: {result.classification} (confidence: {result.confidence:.2f})")
            self.log(f"Reasoning: {result.reasoning}")
    
            return result
    
        except Exception as e:
            self.log(f"Classification failed: {str(e)}")
            raise

    def insert_email(self, priority_email: Priority):
        """Insert classified priority email into the database."""
        DB_FOLDER = r"D:\Projects\inbox-manager\databases"
        DB_NAME = os.path.join(DB_FOLDER, "priority_emails.db")

        os.makedirs(DB_FOLDER, exist_ok=True)
        self.log(f"Database folder ensured at: {DB_FOLDER}")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Updated table schema with classification columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                email_id TEXT PRIMARY KEY,
                from_name TEXT,
                from_email TEXT NOT NULL,
                subject TEXT,
                message TEXT,
                time TEXT,
                classification TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT
            )
        """)
        
        self.log(f"Inserting email: ID={priority_email.email_id}, Subject='{priority_email.subject}'")

        cursor.execute("""
            INSERT OR REPLACE INTO emails
            (email_id, from_name, from_email, subject, message, time, classification, confidence, reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            priority_email.email_id,
            priority_email.from_name,
            priority_email.from_email,
            priority_email.subject,
            priority_email.message,
            priority_email.time,
            priority_email.classification,
            priority_email.confidence,
            priority_email.reasoning
        ))

        conn.commit()
        conn.close()
        self.log(f"Priority email {priority_email.email_id} successfully stored in database")

    def run(self, email: CleanEmailData) -> Priority:
        """Process the email, classify it by priority, and store it in the database."""
        self.log(f"Processing priority email from {email.from_email}")
        
        # Classify the email
        classification_result = self.classifier(email)
        
        # Create Priority object with classification data
        priority_email = Priority(
            email_id=email.email_id,
            from_name=email.from_name,
            from_email=email.from_email,
            subject=email.subject,
            message=email.message,
            time=email.time,
            classification=classification_result.classification,
            confidence=classification_result.confidence,
            reasoning=classification_result.reasoning
        )
        
        # Store in database
        self.insert_email(priority_email)
        
        self.log("Priority email processing completed")
        return priority_email

if __name__ == "__main__":
    
    email = CleanEmailData(
        email_id="19b640e16056d87c",
        from_name="Sarah Johnson",
        from_email="aleeghulami2024@gmail.com",
        subject="URGENT: Server Outage - Immediate Action Required",
        message=(
            "Hello Team,\n\n"
            "We are experiencing a critical server outage affecting all production systems. "
            "Customer-facing services are currently down.\n\n"
            "I need you to join the emergency call immediately at the following link: "
            "https://meet.example.com/emergency\n\n"
            "This requires your immediate attention.\n\n"
            "Best regards,\n"
            "Sarah Johnson\n"
            "IT Operations Manager"
        ),
        time="December 30, 2025, 9:15 AM"
    )

    agent = PriorityAgent()
    result = agent.run(email)
    
    print("\n" + "="*50)
    print("PRIORITY CLASSIFICATION RESULT")
    print("="*50)
    print(f"Email ID: {result.email_id}")
    print(f"Subject: {result.subject}")
    print(f"Classification: {result.classification}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Reasoning: {result.reasoning}")
    print("="*50)