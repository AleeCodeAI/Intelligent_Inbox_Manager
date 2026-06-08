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
    with SessionLocal() as db:
        email = db.query(Email).filter(Email.gmail_id == gmail_id).first()

        if not email:
            return False

        db.delete(email)
        db.commit()
        return True

if __name__ == "__main__":
    gmail_id = "19e6d6fd6decce08"
    did_delete = delete_email(gmail_id)
    if did_delete:
        print(f"email: {gmail_id} deleted successfully.")
    else:
        print(f"email: {gmail_id} not found.")