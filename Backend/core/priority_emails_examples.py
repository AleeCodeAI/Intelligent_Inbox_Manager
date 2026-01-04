
from priority_agent_database import (
    create_db,
    insert_email,
    PriorityEmailData
)

from typing import List

priorities: List[PriorityEmailData] = [
    PriorityEmailData(
        email_id="19b7863a40753757",
        from_name="Dr. Sarah Chen",
        from_email="schen@medicalcenter.com",
        subject="Your Appointment Confirmation - November 15, 2024",
        message="Dear patient, your annual physical examination is scheduled for November 15, 2024 at 2:30 PM at our main clinic. Please arrive 15 minutes early with your insurance card and current medications list. Call 555-1234 to reschedule if needed.",
        time="October 25, 2024, 10:15 AM",
        classification="APPOINTMENT",
        confidence=0.95,
        reasoning="Contains appointment date, time, and preparation instructions"
    ),
    PriorityEmailData(
        email_id="19b787671b9ad02c",
        from_name="Michael Rodriguez",
        from_email="mrodriguez@acmecorp.com",
        subject="Project Timeline Revision Request",
        message="Hi team, I've reviewed the Q4 deliverables and need to push the milestone deadline by one week due to scope changes. Can we schedule a brief call tomorrow to discuss adjustments? Please share your availability.",
        time="November 3, 2024, 3:45 PM",
        classification="CLIENT_COMMUNICATION",
        confidence=0.92,
        reasoning="Direct client request regarding project deliverables and meeting scheduling"
    ),
    PriorityEmailData(
        email_id="19b7879641a137e3",
        from_name="James Wilson",
        from_email="james.wilson@techgiant.com",
        subject="Enterprise License Inquiry - 500+ Users",
        message="We're evaluating enterprise solutions for our global team and your platform came highly recommended. We need licensing for approximately 500 users across 12 offices. Can you provide a customized quote and schedule a demo with your enterprise team? Budget approval is pending but we're looking at the $250K range.",
        time="November 10, 2024, 9:30 AM",
        classification="HIGH_VALUE",
        confidence=0.98,
        reasoning="Large enterprise deal with specific user count and budget mentioned"
    ),
    PriorityEmailData(
        email_id="19b7950632f713e9",
        from_name="Attorney Lisa Park",
        from_email="lpark@lawfirmllp.com",
        subject="CONFIDENTIAL: Settlement Discussion - Case #22-4578",
        message="Pursuant to our privileged communication, attached are the settlement terms for the ongoing litigation. These documents contain sensitive financial information and attorney-client privileged material. Do not forward or distribute without prior written authorization.",
        time="November 5, 2024, 4:20 PM",
        classification="SENSITIVE",
        confidence=0.99,
        reasoning="Contains legal privileged information marked confidential with distribution restrictions"
    ),
    PriorityEmailData(
        email_id="19b7b51b776eece9",
        from_name="Global Services Team",
        from_email="renewals@enterprisesoft.com",
        subject="URGENT: Annual Contract Renewal - $85,000",
        message="Your annual enterprise subscription is up for renewal in 15 days. The renewed contract value is $85,000 for 12 months. Please review the attached agreement and confirm approval by November 20 to avoid service interruption. Let us know if you need any modifications.",
        time="November 1, 2024, 11:00 AM",
        classification="HIGH_VALUE",
        confidence=0.96,
        reasoning="High-value contract renewal with specific dollar amount and urgency"
    )
]

def seed_priority_emails():
    for email in priorities:
        insert_email(email)



# --------------------------
# RUN
# --------------------------
if __name__ == "__main__":
    create_db()
    seed_priority_emails()
    print("DONE")