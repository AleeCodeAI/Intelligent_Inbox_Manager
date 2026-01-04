from priority_direct_send import send_to_n8n
from priority_mark_calendar import mark_calendar
import os 
from dotenv import load_dotenv
from pydantic import BaseModel
from color import Agent 
import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

load_dotenv()

DB_FOLDER = r"D:\Projects\inbox-manager\databases"
os.makedirs(DB_FOLDER, exist_ok=True)
DB_NAME = os.path.join(DB_FOLDER, "priority_emails.db")

class OriginalEmail(BaseModel):
    email_id: str
    from_name: str
    from_email: str
    subject: str
    message: str
    time: str
    classification: str
    confidence: float
    reasoning: str

class CraftedEmail(BaseModel):
    email_id: str
    crafted_email: str
    classification: str
    start: str | None = None  # Already in ISO 8601 format from UI
    end: str | None = None    # Already in ISO 8601 format from UI

class SendPriorityEmail(Agent):
    name = "SendPriorityEmail"
    color = Agent.YELLOW

    # --------------------------------------------------
    # DB FETCH
    # --------------------------------------------------
    def get_email_by_id(self, email_id: str) -> OriginalEmail | None:
        if not os.path.exists(DB_NAME):
            self.log("Database not found")
            return None

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE email_id = ?", (email_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return OriginalEmail(
                email_id=row[0],
                from_name=row[1],
                from_email=row[2],
                subject=row[3],
                message=row[4],
                time=row[5],
                classification=row[6],
                confidence=row[7],
                reasoning=row[8]
            )

        except Exception as e:
            self.log(f"DB error: {e}")
            return None

    # --------------------------------------------------
    # SEND EMAIL (n8n)
    # --------------------------------------------------
    def send_email(self, crafted_email: CraftedEmail) -> dict:
        payload = {
        "id": crafted_email.email_id,
        "body": crafted_email.crafted_email
    }
        self.log(f"Sending email: {crafted_email.email_id}")
        self.log(f"Payload being sent: {payload}")
    
        result = send_to_n8n(payload)
    
        self.log(f"send_to_n8n returned: {result}")  # ADD THIS
    
        return result

    # --------------------------------------------------
    # MAIN PROCESS
    # --------------------------------------------------
    def process_email(self, crafted_email: CraftedEmail) -> dict:
        self.log(f"Processing email ID: {crafted_email.email_id}")

        original_email = self.get_email_by_id(crafted_email.email_id)
        if not original_email:
            return {
                "status": "failed",
                "reason": "Original email not found"
            }

        # ================== APPOINTMENT ==================
        if crafted_email.classification == "APPOINTMENT":
            # Validate start and end times are provided
            if not crafted_email.start or not crafted_email.end:
                return {
                    "status": "failed",
                    "reason": "Start and end times are required for appointments"
                }

            # No parsing needed - UI sends ISO 8601 format directly
            start_iso = crafted_email.start
            end_iso = crafted_email.end

            # Create title from sender's name
            title = f"Appointment with {original_email.from_name}"

            self.log(f"Calendar - Title: {title}, Start: {start_iso}, End: {end_iso}")

            # Mark calendar
            calendar = mark_calendar(
                title=title,
                start=start_iso,
                end=end_iso
            )

            # Check for calendar errors
            if not calendar or calendar.get("status") == "error":
                return {
                    "status": "failed",
                    "reason": "Calendar creation failed",
                    "calendar": calendar,
                    "error": calendar.get("error") if calendar else "No response"
                }

            if calendar.get("status") != "confirmed":
                return {
                    "status": "failed",
                    "reason": "Calendar not confirmed",
                    "calendar": calendar
                }

            # Send email
            send_result = self.send_email(crafted_email)

            return {
                "status": send_result.get("status"),
                "emailId": send_result.get("emailId"),
                "calendar": {
                    "status": calendar.get("status"),
                    "id": calendar.get("id")
                }
            }
        # ================== NON-APPOINTMENT ==================
        send_result = self.send_email(crafted_email)

        # Ensure consistent response format
        if send_result.get("status") == "success":
            self.log(f"Final result being returned: {send_result}")  # ADD THIS
            return {
                "status": "success",
                "emailId": send_result.get("emailId")
            }
        else:
            return {
                "status": "failed",
                "reason": send_result.get("error", "Email sending failed"),
                "emailId": None
            }


if __name__ == "__main__":
    # Example usage
    crafted_email = CraftedEmail(
        email_id="19b7879641a137e3",
        crafted_email="Hi John, thanks for reaching out! I'd be happy to meet tomorrow from 2 PM to 3 PM. See you then!",
        classification="APPOINTMENT",
        start="2026-01-06T14:00:00+05:00",
        end="2026-01-06T15:00:00+05:00"
    )
    
    sender = SendPriorityEmail()
    result = sender.process_email(crafted_email)
    print(result)