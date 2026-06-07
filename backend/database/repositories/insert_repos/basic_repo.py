from database.session import SessionLocal
from database.models.basic import BasicEmailData


def insert_basic(
        email_db_id: str, 
        rag_answer: str = None, 
        rag_status: str = "failed", 
        citations: list[dict] = None,
        failure_reason: str = None,
        needs_manual_reply: bool = False,
        reviewed: bool = False):
    
    db = SessionLocal()
    try:
        record = BasicEmailData(
            email_db_id=email_db_id,
            rag_answer=rag_answer,
            citations=citations,
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

def mark_basic_reviewed(email_db_id: str):
    db = SessionLocal()
    try:
        db.query(BasicEmailData)\
          .filter(BasicEmailData.email_db_id == email_db_id)\
          .update({
              "reviewed": True,
              "needs_manual_reply": False
          })

        db.commit()

    finally:
        db.close()