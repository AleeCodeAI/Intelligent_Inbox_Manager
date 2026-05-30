from database.session import SessionLocal
from database.models.email import Email


def get_all_emails() -> list[dict]:
    """
    Endpoint 10 — All emails from the main emails table.
    Used in the analysis dashboard.
    """
    db = SessionLocal()
    results = db.query(Email).all()

    return [
        {
            "email_db_id": email.email_db_id,
            "gmail_id": email.gmail_id,
            "thread_id": email.thread_id,
            "sender_name": email.sender_name,
            "sender_email": email.sender_email,
            "subject": email.subject,
            "body": email.body,
        }
        for email in results
    ]

if __name__ == "__main__":
    import json

    emails = get_all_emails()
    print(json.dumps(emails, indent=2))