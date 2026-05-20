from database.session import SessionLocal
from database.models.email import Email 


def insert_email(id: str, 
                 email_id: str, 
                 thread_id: str, 
                 sender_name: str, 
                 sender_email: str, 
                 subject: str, 
                 body: str):
    
    db = SessionLocal()
    try:
        # Note: The model uses 'id' as primary key, not 'email_id'
        email = Email(
            id=id,  # This should be a unique ID for the email record
            email_id=email_id,  # This is the actual email ID from the email service
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

def get_email(db, email_id: str):
    return (
        db.query(Email)
        .filter(Email.email_id == email_id)
        .first()
    )