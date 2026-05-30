from database.session import SessionLocal
from database.models.email import Email
from database.models.priority import PriorityEmailData


def get_priority_unreviewed() -> list[dict]:
    """
    High-priority emails that have not yet been reviewed by admin.
    Returns emails where reviewed=False in the priority_email_data table.
    """
    db = SessionLocal()
    results = (
        db.query(Email, PriorityEmailData)
        .join(PriorityEmailData, Email.email_db_id == PriorityEmailData.email_db_id)
        .filter(PriorityEmailData.reviewed.is_(False))
        .order_by(PriorityEmailData.confidence.desc())
        .all()
    )

    return [
        {
            "email_db_id": email.email_db_id,
            "gmail_id": email.gmail_id,
            "thread_id": email.thread_id,
            "sender_name": email.sender_name,
            "sender_email": email.sender_email,
            "subject": email.subject,
            "body": email.body,
            "priority_type": priority.priority_type,
            "confidence": priority.confidence,
            "reasoning": priority.reasoning,
            "reviewed": priority.reviewed,
        }
        for email, priority in results
    ]

if __name__ == "__main__":
    import json
    emails = get_priority_unreviewed()
    print(json.dumps(emails, indent=2))