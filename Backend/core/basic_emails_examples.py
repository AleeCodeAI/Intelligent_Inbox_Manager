import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
import random

# --------------------------
# Import your DB functions
# --------------------------
from basic_agent_database import create_db, insert_email
# --------------------------
# Pydantic Model (matches DB)
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

emails: List[CleanEmailData] = [
    CleanEmailData(
        email_id="19b7863a40753757",
        from_name="Thomas Wilson",
        from_email="thomas.wilson@gmail.com",
        subject="Consultation Pricing Inquiry",
        message="Hello, I'm interested in your personal consulting services. Could you provide information about your hourly rates, package options, and availability for new clients? Do you offer free introductory calls?",
        time="2024-03-15 09:30:00"
    ),
    CleanEmailData(
        email_id="19b787671b9ad02c",
        from_name="Maria Rodriguez",
        from_email="maria.rodriguez@yahoo.com",
        subject="Question About Your Privacy Policy",
        message="I'm considering using your services but have concerns about data privacy. Can you share your privacy policy details? Specifically, how do you handle client data, what information is stored, and do you share data with third parties?",
        time="2024-03-16 14:20:00"
    ),
    CleanEmailData(
        email_id="19b7879641a137e3",
        from_name="David Chen",
        from_email="david.chen@outlook.com",
        subject="Background and Qualifications Inquiry",
        message="Before proceeding with your services, I'd like to know more about your professional background. What certifications do you hold? How many years of experience? Could you provide some client references or case studies?",
        time="2024-03-14 11:45:00"
    ),
    CleanEmailData(
        email_id="19b7950632f713e9",
        from_name="Sarah Johnson",
        from_email="sarah.johnson@gmail.com",
        subject="Service Packages and Pricing Breakdown",
        message="I've reviewed your website and am interested in your premium package. Could you provide a detailed breakdown of what's included? Also, what's your cancellation policy and are there any hidden fees?",
        time="2024-03-17 16:10:00"
    ),
    CleanEmailData(
        email_id="19b7b51b776eece9",
        from_name="Robert Kim",
        from_email="r.kim@protonmail.com",
        subject="Refund and Guarantee Policy",
        message="What is your satisfaction guarantee policy? If I'm not happy with the service, what's the refund process? Do you offer partial refunds for work already completed?",
        time="2024-03-13 13:55:00"
    )
]

def seed_emails():
    for email in emails:
        insert_email(email)
# --------------------------
# Run Seeder
# --------------------------
if __name__ == "__main__":
    create_db()
    seed_emails()
