import os 
from dotenv import load_dotenv
from openai import OpenAI 
from agents.basic_agent.rag.answer import DB_NAME, AnswerQuestion
from pydantic import BaseModel, Field
from typing import Optional
import sqlite3
from agents.basic_agent.send_email import send_to_n8n
from Backend.color import Agent
import logging 

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

load_dotenv(override=True)
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")

SYSTEM_PROMPT = """ 
You are an AI Assistant that will craft the final response to the email sent to the recipient on behalf of Alee who is an Applied
AI Engineer. 

You will be provided with email content and the reply to the email sent to the user. You are responsible to take this information 
and generate a concise and formal email response to the recipient.

**CRITICAL: The body MUST be formatted as valid HTML suitable for email clients. Use inline CSS styles for formatting.**

EXAMPLE:
Email Content:
recipient: Sarah Johnson <sarah.johnson@techcorp.com>
reply:
As an Applied AI Engineer, I have expertise in:
- Applied Artificial Intelligence (end‑to‑end AI system design)  
- Large Language Models (prompt engineering, evaluation, integration)  
- Retrieval‑Augmented Generation (knowledge‑base design, embedding pipelines, retrieval logic)  
- Agentic AI Systems (multi‑agent workflows, tool usage, automation)

Final Email Response:

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px;">
                <p style="margin: 0 0 15px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                    Dear Sarah Johnson,
                </p>
                
                <p style="margin: 0 0 15px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                    Thank you for your message.
                </p>
                
                <p style="margin: 0 0 15px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                    As an Applied AI Engineer, I specialize in designing and delivering end-to-end AI systems. My expertise includes:
                </p>
                
                <ul style="margin: 0 0 15px 0; padding-left: 20px; font-size: 16px; line-height: 1.8; color: #333333;">
                    <li style="margin-bottom: 8px;"><strong>Large Language Models</strong> (prompt engineering, evaluation, and integration)</li>
                    <li style="margin-bottom: 8px;"><strong>Retrieval-Augmented Generation</strong> (knowledge-base design, embedding pipelines, and retrieval logic)</li>
                    <li style="margin-bottom: 8px;"><strong>Agentic AI systems</strong> (multi-agent workflows, tool usage, and automation)</li>
                </ul>
                
                <p style="margin: 0 0 15px 0; font-size: 16px; line-height: 1.6; color: #333333;">
                    I would be happy to discuss how these capabilities can support your needs or explore potential collaboration.
                </p>
                
                <p style="margin: 20px 0 0 0; font-size: 16px; line-height: 1.6; color: #333333;">
                    Best regards,<br>
                    <strong>Alee</strong>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>

HTML FORMATTING RULES:
1. Always use table-based layouts for email compatibility
2. Use inline CSS styles (no external stylesheets or <style> tags)
3. Keep font sizes readable (14-16px for body text)
4. Use proper spacing with margin and padding
5. Structure content with <p>, <ul>, <li>, <strong>, <h3> tags as needed
6. Maintain professional color scheme (#333333 for text, #2c3e50 for headings)
7. Ensure proper line-height (1.6-1.8) for readability
8. Always include DOCTYPE, html, head, and body tags
"""


class EmailResponse(BaseModel):
    body: str = Field(description="The body content of the email.")

class Email(BaseModel):
    from_name: Optional[str] = Field(description="Name of the email sender.")
    message: str = Field(description="Content of the email message.")
    reply: str = Field(description="Reply content for the email.")

class CleanEmailData(BaseModel):
    """Pydantic model for cleaned email data."""
    email_id: str = Field(description="Unique identifier for the email.")
    from_name: Optional[str] = None
    from_email: str = Field(description="Sender's email address.")
    subject: str = Field(description="The subject of the email.")
    message: str = Field(description="The cleaned body content of the email.")
    time: str = Field(description="Human-readable timestamp of the email.")

print("heheheheh")

class BasicAgent(Agent):
    name = "BasicAgent"
    color = Agent.GREEN
    
    def __init__(self):
        self.client = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)
        self.answer_question = AnswerQuestion()
        self.system_prompt = SYSTEM_PROMPT
        self.log("Initialized BasicAgent")
    
    def insert_email(self, email: CleanEmailData):
        """Insert email into the database."""

        DB_FOLDER = r"D:\Projects\inbox-manager\databases"
        DB_NAME = os.path.join(DB_FOLDER, "basic_emails.db")
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

    def send_email(self, email, reply):
        data = {"id": email.email_id, "body": reply.body}
        result = send_to_n8n(data)
        self.log(f"EMAIL'S STATUS: {result['status']} EMAIL ID: {result['emailId']}")


    def rag(self, email):
        self.log(f"Running RAG for email from {email.from_email}")
        reply, chunks = self.answer_question.answer_question(email.message)
        return reply

    def prepare_email(self, email):
        return Email(
            from_name=email.from_name,
            message=email.message,
            reply=self.rag(email)
        )

    def make_user_message(self, email):
        email_obj = self.prepare_email(email)
        return (
            f"Recipient Name: {email_obj.from_name}\n"
            f"Recipient Email: {email.from_email}\n\n"
            f"Message Content: {email_obj.message}\n\n"
            f"Reply: {email_obj.reply}\n\n"
            f"Final Email Response:"
        )

    def make_messages(self, email):
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.make_user_message(email)}
        ]
    def generate_email_response(self, email) -> EmailResponse:
        self.log(f"Generating email response for {email.email_id}")
        raw_response = self.client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL"),
            messages=self.make_messages(email)
        )
        content = raw_response.choices[0].message.content
        try:
            final_reply = EmailResponse.model_validate_json(content)
        except Exception:
        # Fallback: treat as raw HTML
            final_reply = EmailResponse.model_validate({"body": content})
        self.send_email(email, final_reply)
        return final_reply

    def run(self, email):
        self.log(f"Processing email {email.email_id} from {email.from_email}")
        try:
           email_response = self.generate_email_response(email)
           self.log(f"Successfully processed email {email.email_id}")
           return email_response

        except Exception as e:
           self.log(f"Error processing email {email.email_id}: {str(e)}")
           self.insert_email(email)
           # Optionally return a fallback response
           return EmailResponse(
              body=(
                "The system could not generate an automatic response for this email.\n"
                "The email has been saved and will require manual handling."))

if __name__ == "__main__":

# Example with fake data
    email = CleanEmailData(
        email_id="19b640e16056d87c",
        from_name="Ali Khan",
        from_email="aleeghulami2024@gmail.com",
        subject="Inquiry About AI Consulting & Mentorship Scope",
        message=(
        "Hello Alee,\n\n"
        "I came across your work in applied AI and wanted to clarify a few things "
        "before reaching out further.\n\n"
        "I'm currently exploring a product idea involving LLMs and RAG, and I'm "
        "looking for architectural guidance rather than full product development. "
        "I value practical, maintainable systems and prefer working with someone "
        "who focuses on real-world usefulness over theory.\n\n"
        "Could you share whether you offer paid mentorship or consulting in areas "
        "like applied AI system design, agent-based architectures, or RAG pipelines? "
        "I'm especially interested in understanding your availability and what "
        "types of engagements you typically respond to.\n\n"
        "Happy to provide more context about the project if helpful.\n\n"
        "Best regards,\n"
        "Ali Khan"
    ),
    time="2024-12-29 16:08:42")

    agent = BasicAgent()
    email_response = agent.run(email)
    print(f"Body: {email_response.body}")