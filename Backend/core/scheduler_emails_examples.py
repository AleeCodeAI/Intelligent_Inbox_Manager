import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel

# --------------------------
# IMPORT YOUR DB FUNCTIONS
# --------------------------
from scheduler_agent_database import create_db, insert_email
# ⚠️ Replace with your actual filename
# Example:
# from scheduler_db import create_db, insert_email


# --------------------------
# Pydantic model (matches DB)
# --------------------------
class CleanEmailData(BaseModel):
    email_id: str
    from_name: str
    from_email: str
    subject: str
    message: str
    time: str


from datetime import datetime
from typing import List

# Using March 2024 as current month (you can adjust as needed)
current_year = datetime.now().year
current_month = datetime.now().month

emails: List[CleanEmailData] = [
    CleanEmailData(
        email_id="19b7863a40753757",
        from_name="Alex Johnson",
        from_email="alex.johnson@techcorp.com",
        subject="Q1 Project Status Update",
        message="Hi team, attached is the Q1 project status report. We're on track for the April 15 deadline. Let me know if you have any questions about the deliverables.",
        time="2024-03-05 14:30:00"
    ),
    CleanEmailData(
        email_id="19b787671b9ad02c",
        from_name="Marketing Team",
        from_email="newsletter@company.com",
        subject="Monthly Newsletter - March Edition",
        message="Welcome to our March newsletter! This month features new product launches, upcoming webinars, and team spotlights. Read the full edition at our company portal.",
        time="2024-03-01 09:00:00"
    ),
    CleanEmailData(
        email_id="19b7879641a137e3",
        from_name="Sarah Chen",
        from_email="schen@partners.org",
        subject="Meeting Follow-up from March 10",
        message="Thanks for the productive meeting yesterday. Here's the summary of action items: 1. Draft proposal by March 15, 2. Review budget spreadsheet, 3. Schedule follow-up for March 20.",
        time="2024-03-11 11:15:00"
    ),
    CleanEmailData(
        email_id="19b7950632f713e9",
        from_name="IT Support",
        from_email="support@company-it.com",
        subject="System Maintenance Scheduled - March 16, 2-4 AM",
        message="Notice: We will perform scheduled system maintenance on Saturday, March 16 from 2:00 AM to 4:00 AM UTC. Services may be temporarily unavailable. Plan your work accordingly.",
        time="2024-03-08 16:45:00"
    ),
    CleanEmailData(
        email_id="19b7b51b776eece9",
        from_name="Michael Rodriguez",
        from_email="m.rodriguez@clientco.com",
        subject="New Feature Request",
        message="We'd like to request a new dashboard feature showing real-time analytics. Could you provide an estimate for implementation in your next sprint? Our team can provide specs by March 18.",
        time="2024-03-12 13:20:00"
    )
]

# To get actual current month dynamically:
# from datetime import datetime
# current_month = datetime.now().strftime("%B")  # "March"
# current_year = datetime.now().year

def seed_scheduler_emails():
    for email in emails:
        insert_email(email)

# --------------------------
# RUN
# --------------------------
if __name__ == "__main__":
    create_db()
    seed_scheduler_emails()
