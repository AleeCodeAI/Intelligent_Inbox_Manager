from database.session import SessionLocal
from database.models.email import Email 


def insert_email(email_db_id: str, 
                 gmail_id: str, 
                 thread_id: str, 
                 sender_name: str, 
                 sender_email: str, 
                 subject: str, 
                 body: str):
    
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

        return email

    finally:
        db.close()

def get_email(db, gmail_id: str):
    return (
        db.query(Email)
        .filter(Email.gmail_id == gmail_id)
        .first()
    )