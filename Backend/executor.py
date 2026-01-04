import os
import logging
import json
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Internal imports (assuming these exist in your project structure)
from core.preprocessor import EmailPreprocessor
from core.receive_email import ReceiveEmail
from agents.basic_agent.basic_agent import BasicAgent
from agents.scheduler_agent.scheduler_agent import SchedulerAgent
from agents.priority_agent.priority_agent import PriorityAgent
from agents.nonbusiness_agent.nonbusiness_agent import NonBusinessAgent
from color import Agent

# Setup basic logging for the module
logging.basicConfig(level=logging.INFO, format='%(message)s')

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

class Executer(BaseModel):
    classification: str = Field(description="the agent that shall handle a task")
    confidence: float = Field(description="the confidence level of how certain the model is for the classification made")
    reasoning: str = Field(description="precise explanation of why a certain classification is made")

class Result(BaseModel):
    email_id: str = Field(description="Unique identifier for the email.")
    from_name: Optional[str] = None
    from_email: str = Field(description="Sender's email address.")
    subject: str = Field(description="The subject of the email.")
    message: str = Field(description="The cleaned body content of the email.")
    time: str = Field(description="Human-readable timestamp of the email.")
    classification: str = Field(description="the agent that shall handle a task")
    confidence: float = Field(description="the confidence level of how certain the model is for the classification made")
    reasoning: str = Field(description="precise explanation of why a certain classification is made")
    success: bool = Field(description="indicates success if the pipeline completed successfully (True/False)")

SYSTEM_PROMPT = """ 
You are an intelligent email classification agent. Your ONLY task is to analyze an incoming email and classify it into exactly ONE of the 
following categories: BASIC, SCHEDULER, PRIORITY, or NON_BUSINESS.

You must respond with ONLY a valid JSON object in this exact format:
{
  "classification": "BASIC" | "SCHEDULER" | "PRIORITY" | "NON_BUSINESS",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why this classification was chosen"
}

CLASSIFICATION DEFINITIONS

BASIC:
Use BASIC for general informational or non-urgent business emails, including:
- Questions about expertise, skills, background, or experience
- Inquiries about services offered
- Policies, terms, conditions, FAQs
- General business questions that do not require a meeting or urgent action

Examples:
- "What are your areas of expertise?"
- "Do you work with Python and TensorFlow?"
- "Can you tell me about your past projects?"

SCHEDULER:
Use SCHEDULER for business emails that would benefit from a meeting or appointment, including:
- Explicit meeting requests (e.g., schedule a meeting, set up a call)
- Implicit scheduling needs (complex discussions, architectural decisions, project clarification)
- Project inquiries with value below $5,000

Examples:
- "Can we discuss this over a call?"
- "I'd like to talk about implementing a chatbot"
- "Small ML project, budget around $3,000"

PRIORITY:
Use PRIORITY for high-stakes, sensitive, or time-critical business matters, including:
- Appointment confirmations or acceptances
- Ongoing communications from current clients
- Project inquiries valued at $5,000 or more
- Legal, financial, contractual, or compliance issues
- Bank notifications

Examples:
- "Confirming our meeting tomorrow at 9 AM"
- "Enterprise AI project, budget $30,000"
- "There's an issue with the invoice"
- "Copyright or licensing concern"

NON_BUSINESS:
Use NON_BUSINESS for emails that are not related to professional work or business activities, including:
- Personal emails from friends or family
- Marketing emails and promotional offers
- Newsletters and subscriptions
- Social media notifications
- Spam or unsolicited bulk emails
- Shopping receipts and order confirmations
- Entertainment or social event invitations (non-professional)

Examples:
- "50% off sale this weekend!"
- "Your Amazon order has shipped"
- "Join us for our birthday party"
- "Your Netflix subscription is expiring"
- "Congratulations! You've won..."
- "New post from your friend on Facebook"

DECISION PROCESS

1. Read the entire email carefully
2. Identify the primary intent and context
3. Check if it's NON_BUSINESS first (personal, promotional, spam)
4. If business-related, check for PRIORITY triggers
5. If not PRIORITY, check for SCHEDULER triggers
6. If neither applies, classify as BASIC
7. Assign a confidence score based on rule strength

CONFIDENCE SCORING RULES

- 0.9–1.0: Explicit and unambiguous rule match
- 0.75–0.89: Implicit but clear intent
- 0.6–0.74: Some ambiguity, best-fit classification
- 0.4–0.59: High ambiguity

Do NOT use 0.0 unless the email is extremely unclear.

EDGE CASE RULES

- Multiple intents: PRIORITY > SCHEDULER > BASIC > NON_BUSINESS
- Ambiguous budget:
  - Implied high value or enterprise scope → PRIORITY
  - Small or unclear scope → SCHEDULER
- Urgency alone does NOT imply PRIORITY
  - Urgent generic question → BASIC
  - Urgent meeting request → SCHEDULER
  - Urgent payment or legal issue → PRIORITY
- Follow-ups:
  - Confirming a meeting → PRIORITY
  - Following up on ongoing work → PRIORITY
  - Following up on unconfirmed scheduling → SCHEDULER
- Mixed content:
  - If email contains both business and non-business elements, prioritize business classification
  - Pure promotional/marketing with no business inquiry → NON_BUSINESS

STRICT RULES

- Always output valid JSON only
- Always choose exactly one classification
- Confidence must reflect certainty level and must not default to 0
- When unsure between BASIC and SCHEDULER, choose SCHEDULER
- When unsure between SCHEDULER and PRIORITY, choose PRIORITY
- When clearly non-business (promotional, personal, spam), choose NON_BUSINESS
- Never add explanations outside the JSON

Now analyze the incoming email and return your classification.

"""

class ExecuterAgent(Agent):
    name = "ExecutorAgent"
    color = Agent.MAGENTA
    
    def __init__(self):
        self.preprocessor = EmailPreprocessor()
        self.receive_email = ReceiveEmail()
        self.basic_agent = BasicAgent()
        self.scheduler_agent = SchedulerAgent()
        self.priority_agent = PriorityAgent()
        self.nonbusiness_agent = NonBusinessAgent()
        self.client = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)
        self.memory_path = r"D:\Projects\inbox-manager\databases\memory.jsonl"
        self.log("ExecutorAgent initialized successfully")

    def user(self, email):
        return f""" 
            here is the email to classify:
            {email.message}"""

    def classifier(self, email):
        self.log(f"Starting classification for email_id={email.email_id}")
        self.log(f"Email subject: '{email.subject}' from {email.from_email}")
        
        try:
            response = self.client.chat.completions.parse(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": self.user(email)},
                ],
                response_format=Executer
            )
            
            result = response.choices[0].message.parsed
            self.log(f"Classification complete: {result.classification} (confidence: {result.confidence:.2f})")
            self.log(f"Reasoning: {result.reasoning}")
            
            return result
            
        except Exception as e:
            self.log(f"Classification failed: {str(e)}")
            raise

    def save_to_memory(self, result: Result):
        self.log(f"Saving result to memory.jsonl for email_id={result.email_id}")
        try:
            with open(self.memory_path, "a", encoding="utf-8") as f:
                f.write(result.model_dump_json() + "\n")
            self.log("Result saved successfully")
        except Exception as e:
            self.log(f"Failed to save to memory: {str(e)}")
            raise

    def run(self):
        self.log("=" * 60)
        self.log("Executor run started")
        self.log("=" * 60)
        
        try:
            # Phase 1: Fetch emails
            self.log("Phase 1: Fetching unread emails")
            raw_email = self.receive_email.fetch_unread_emails(max_results=1)

            # Phase 2: Preprocess emails
            self.log("Phase 2: Preprocessing emails")
            cleaned_emails = self.preprocessor.process_email_response(raw_email)
            self.log(f"Preprocessed {len(cleaned_emails.emails)} email(s)")
            
            if not cleaned_emails.emails:
                self.log("No emails to process")
                return
            
            # Phase 3: Process each email
            self.log(f"Phase 3: Processing {len(cleaned_emails.emails)} email(s)")
            
            for idx, email in enumerate(cleaned_emails.emails, 1):
                self.log("-" * 60)
                self.log(f"Processing email {idx}/{len(cleaned_emails.emails)}")
                self.log(f"Email ID: {email.email_id}")
                self.log(f"From: {email.from_name} <{email.from_email}>")
                self.log(f"Subject: {email.subject}")
                
                try:
                    # Phase 3a: Classification
                    self.log("Phase 3a: Classifying email")
                    classification = self.classifier(email)
                    
                    # Phase 3b: Route to appropriate agent
                    self.log(f"Phase 3b: Routing to {classification.classification} agent")
                    
                    if classification.classification == "BASIC":
                        self.log("Delegating to BasicAgent")
                        self.basic_agent.run(email)
                    elif classification.classification == "SCHEDULER":
                        self.log("Delegating to SchedulerAgent")
                        self.scheduler_agent.run(email)
                    elif classification.classification == "PRIORITY":
                        self.log("Delegating to PriorityAgent")
                        self.priority_agent.run(email)
                    elif classification.classification == "NON_BUSINESS":
                        self.log("Delegating to NonBusinessAgent")
                        self.nonbusiness_agent.run(email)
                    else:
                        raise ValueError(f"Invalid classification: {classification.classification}")
                    
                    # Phase 3c: Create and save result
                    self.log("Phase 3c: Creating result record")
                    result = Result(
                        email_id=email.email_id,
                        from_name=email.from_name,
                        from_email=email.from_email,
                        subject=email.subject,
                        message=email.message,
                        time=email.time,
                        classification=classification.classification,
                        confidence=classification.confidence,
                        reasoning=classification.reasoning,
                        success=True
                    )
                    
                    self.save_to_memory(result)
                    self.log(f"✓ Email {email.email_id} processed successfully")

                except Exception as e:
                    self.log(f"✗ Pipeline failed for email_id={email.email_id}")
                    self.log(f"Error details: {str(e)}")
                    
                    failed_result = Result(
                        email_id=email.email_id,
                        from_name=email.from_name,
                        from_email=email.from_email,
                        subject=email.subject,
                        message=email.message,
                        time=email.time,
                        classification="ERROR",
                        confidence=0.0,
                        reasoning=str(e),
                        success=False
                    )
                    
                    self.save_to_memory(failed_result)
            
            self.log("=" * 60)
            self.log("Executor run completed successfully")
            self.log("=" * 60)
            
        except Exception as e:
            self.log(f"✗ Executor run failed: {str(e)}")
            raise

if __name__ == "__main__":
    executor = ExecuterAgent()
    executor.run()
    print("FINISHED")