from database.session import SessionLocal
from database.models.nonbusiness import NonBusinessEmailData


def insert_nonbusiness(email_id: str, reason: str, notes: str = None):
    db = SessionLocal()
    try:
        record = NonBusinessEmailData(
            email_id=email_id,
            reason=reason,
            notes=notes,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()

def mark_nonbusiness_reviewed(db, email_db_id: str):
    db.query(NonBusinessEmailData)\
      .filter(NonBusinessEmailData.email_id == email_db_id)\
      .update({"reviewed": True})
    db.commit()