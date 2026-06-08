from database.session import SessionLocal
from database.models.email import Email
from database.models.nonbusiness import NonBusinessEmailData


def get_nonbusiness_unreviewed() -> list[dict]:
    """
    Non-business emails that have not yet been reviewed by admin.
    Returns emails where reviewed=False in the nonbusiness_email_data table.
    """
    with SessionLocal() as db:
        results = (
            db.query(Email, NonBusinessEmailData)
            .join(NonBusinessEmailData, Email.email_db_id == NonBusinessEmailData.email_db_id)
            .filter(NonBusinessEmailData.reviewed.is_(False))
            .order_by(NonBusinessEmailData.confidence.desc())
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
                "nonbusiness_type": nonbusiness.nonbusiness_type,
                "confidence": nonbusiness.confidence,
                "reasoning": nonbusiness.reasoning,
                "reviewed": nonbusiness.reviewed,
            }
            for email, nonbusiness in results
        ]


if __name__ == "__main__":
    import json
    emails = get_nonbusiness_unreviewed()
    print(json.dumps(emails, indent=2))