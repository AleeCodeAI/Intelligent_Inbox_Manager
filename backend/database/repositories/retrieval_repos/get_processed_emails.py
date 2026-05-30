from database.session import SessionLocal
from database.models.email import Email
from database.models.processing import EmailProcessing


def get_all_email_processing() -> list[dict]:
    """
    Endpoint 11 — All records from the email_processing table joined with emails.
    Used in the analysis dashboard.
    """
    db = SessionLocal()
    results = (
        db.query(EmailProcessing, Email)
        .join(Email, EmailProcessing.email_db_id == Email.email_db_id)
        .all()
    )

    return [
        {
            "email_processing_id": processing.email_processing_id,
            "email_db_id": processing.email_db_id,
            "classification": processing.classification,
            "confidence": processing.confidence,
            "reasoning": processing.reasoning,
            "success": processing.success,
            "processed_date": processing.processed_date,
            "sender_name": email.sender_name,
            "sender_email": email.sender_email,
            "subject": email.subject,
            "body": email.body,
            "gmail_id": email.gmail_id,
            "thread_id": email.thread_id,
        }
        for processing, email in results
    ]

if __name__ == "__main__":
    import json
    email_processing_records = get_all_email_processing()
    print(json.dumps(email_processing_records, indent=2))