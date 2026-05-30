from database.session import SessionLocal
from database.models.priority import PriorityEmailData
from schemas import PriorityResult


def insert_priority(
    email_db_id: str,
    data: PriorityResult,
    reviewed: bool = False
):
    db = SessionLocal()

    try:
        record = PriorityEmailData(
            email_db_id=email_db_id,
            priority_type=data.priority_type,
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


def mark_priority_reviewed(email_db_id: str):
    db = SessionLocal()

    try:
        db.query(PriorityEmailData)\
          .filter(PriorityEmailData.email_db_id == email_db_id)\
          .update({"reviewed": True})

        db.commit()

    finally:
        db.close()