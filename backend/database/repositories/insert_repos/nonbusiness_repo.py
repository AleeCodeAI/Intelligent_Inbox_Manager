from database.session import SessionLocal
from database.models.nonbusiness import NonBusinessEmailData
from schemas import NonBusinessResult

def insert_nonbusiness(
    email_db_id: str,
    data: NonBusinessResult,
    reviewed: bool = False
):
    db = SessionLocal()

    try:
        record = NonBusinessEmailData(
            email_db_id=email_db_id,
            nonbusiness_type=data.nonbusiness_type,
            confidence=data.confidence,
            reasoning=data.reasoning,
            reviewed=reviewed
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()

def mark_nonbusiness_reviewed(db, email_db_id: str):
    db.query(NonBusinessEmailData)\
      .filter(NonBusinessEmailData.email_db_id == email_db_id)\
      .update({"reviewed": True})
    db.commit()