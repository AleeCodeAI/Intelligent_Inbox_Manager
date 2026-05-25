from database.session import SessionLocal
from database.models.email import Email


def insert_email(
    email_db_id, gmail_id, thread_id, sender_name, sender_email, subject, body
):
    db = SessionLocal()
    try:
        email = Email(
            email_db_id=email_db_id,
            gmail_id=gmail_id,
            thread_id=thread_id,
            sender_name=sender_name,
            sender_email=sender_email,
            subject=subject,
            body=body,
        )

        db.add(email)
        db.commit()
        db.refresh(email)

        # Sanity check
        check = db.query(Email).filter(Email.gmail_id == gmail_id).first()
        print(
            f"[DB CHECK] Row exists after commit: {check is not None} | gmail_id: {gmail_id}"
        )

        return email

    finally:
        db.close()


def get_email_by_thread(thread_id: str):
    db = SessionLocal()
    try:
        return db.query(Email).filter(Email.thread_id == thread_id).first()
    finally:
        db.close()
