from database.session import SessionLocal
from database.models.email import Email


def delete_email(gmail_id: str) -> bool:
    """
    Delete an email by gmail_id.
    Removes the row from emails table — CASCADE automatically deletes
    the matching rows in basic_email_data, priority_email_data,
    nonbusiness_email_data, appointments, and email_processing.
    Returns True if deleted, False if not found.
    """
    db = SessionLocal()
    email = db.query(Email).filter(Email.gmail_id == gmail_id).first()

    if not email:
        return False

    db.delete(email)
    db.commit()

    return True

if __name__ == "__main__":
    gmail_id = "19e6d6fd6decce08"
    delete_email(gmail_id)
    print(f"email: {gmail_id} deleted")