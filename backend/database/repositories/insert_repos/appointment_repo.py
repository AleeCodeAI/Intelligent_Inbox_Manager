from database.session import SessionLocal
from database.models.appointment import Appointment
from schemas import Appointment as AppointmentSchema

def insert_appointment(data: AppointmentSchema):
    db = SessionLocal()

    try:
        record = Appointment(
            email_db_id=data.email_db_id,
            event_id=data.event_id,
            event_title=data.event_title,
            event_start=data.event_start,
            event_end=data.event_end,
            calendar_status=data.calendar_status,
            confirmation_email_status=data.confirmation_email_status
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()