from database.session import SessionLocal
from database.models.priority import PriorityEmailData


def insert_priority(email_db_id: str, 
                    priority_type: str, 
                    reviewed: bool = False):
    
    db = SessionLocal()
    try:
        record = PriorityEmailData(
            email_db_id=email_db_id,
            priority_type=priority_type,
            reviewed=reviewed
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()

def mark_priority_reviewed(db, email_db_id: str):
    db.query(PriorityEmailData)\
      .filter(PriorityEmailData.email_db_id == email_db_id)\
      .update({"reviewed": True})
    db.commit()