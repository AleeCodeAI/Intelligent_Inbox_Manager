from database.session import SessionLocal
from database.models.priority import PriorityEmailData


def insert_priority(email_id: str, priority_type: str, client_tier: str):
    db = SessionLocal()
    try:
        record = PriorityEmailData(
            email_id=email_id,
            priority_type=priority_type,
            client_tier=client_tier,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()