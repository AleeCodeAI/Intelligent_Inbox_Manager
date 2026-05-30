from database.session import SessionLocal
from database.models.email import Email
from database.models.basic import BasicEmailData


def get_basic_manual_pending() -> list[dict]:
    """
    Basic emails where RAG failed and manual reply is pending.
    Returns emails where needs_manual_reply=True and reviewed=False.
    """
    db = SessionLocal()
    results = (
        db.query(Email, BasicEmailData)
        .join(BasicEmailData, Email.email_db_id == BasicEmailData.email_db_id)
        .filter(
            BasicEmailData.needs_manual_reply.is_(True),
            BasicEmailData.reviewed.is_(False),
        )
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
            "rag_status": basic.rag_status,
            "failure_reason": basic.failure_reason,
            "rag_answer": basic.rag_answer,
            "citations": basic.citations,
            "needs_manual_reply": basic.needs_manual_reply,
            "reviewed": basic.reviewed,
        }
        for email, basic in results
    ]

if __name__ == "__main__":
    import json
    emails = get_basic_manual_pending()
    print(json.dumps(emails, indent=2))