from database.session import SessionLocal
from database.models.email import Email
from schemas import InboundEmail  


def insert_email(data: InboundEmail):
    db = SessionLocal()
    try:
        email = Email(
            id=data.id,
            thread_id=data.thread_id,
            sender_name=data.sender_name,
            sender_email=data.sender_email,
            subject=data.subject,
            body=data.body,
        )

        db.add(email)
        db.commit()
        db.refresh(email)

        return email

    finally:
        db.close()