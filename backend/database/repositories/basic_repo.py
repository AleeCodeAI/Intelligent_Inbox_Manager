from database.session import SessionLocal
from database.models.basic import BasicEmailData


def insert_basic(
        email_id: str, 
        rag_response: str = None, 
        rag_status: str = "failed", 
        failure_reason: str = None,
        needs_manual_reply: bool = False,
        reviewed: bool = False):
    
    db = SessionLocal()
    try:
        record = BasicEmailData(
            email_id=email_id,
            rag_response=rag_response,
            rag_status=rag_status,
            failure_reason=failure_reason,
            needs_manual_reply=needs_manual_reply,
            reviewed=reviewed
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()

def mark_basic_reviewed(db, email_db_id: str):
    db.query(BasicEmailData)\
      .filter(BasicEmailData.email_id == email_db_id)\
      .update({"reviewed": True})
    db.commit()