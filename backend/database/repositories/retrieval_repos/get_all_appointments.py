from database.session import SessionLocal
from database.models.email import Email
from database.models.appointment import Appointment


def get_all_appointments() -> list[dict]:
    """
    Endpoint 12 — All appointments joined with their originating email.
    """
    db = SessionLocal()
    results = (
        db.query(Appointment, Email)
        .join(Email, Appointment.email_db_id == Email.email_db_id)
        .all()
    )

    return [
        {
            "email_db_id": appointment.email_db_id,
            "event_id": appointment.event_id,
            "event_title": appointment.event_title,
            "event_start": appointment.event_start,
            "event_end": appointment.event_end,
            "calendar_status": appointment.calendar_status,
            "confirmation_email_status": appointment.confirmation_email_status,
            "created_at": appointment.created_at,
            "sender_name": email.sender_name,
            "sender_email": email.sender_email,
            "subject": email.subject,
            "body": email.body,
            "gmail_id": email.gmail_id,
            "thread_id": email.thread_id,
        }
        for appointment, email in results
    ]

if __name__ == "__main__":
    import json
    from datetime import datetime

    def serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type not serializable: {type(obj)}")

    appointments = get_all_appointments()
    print(json.dumps(appointments, indent=2, default=serializer))