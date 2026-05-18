from database.session import SessionLocal
from database.models.processing import EmailProcessing
from schemas import EmailProcessed


def insert_processing(email_id: str, data: EmailProcessed):
    db = SessionLocal()
    try:
        record = EmailProcessing(
            id=f"proc_{email_id}",  
            email_id=email_id,
            classification=data.classification,
            confidence=data.confidence,
            reasoning=data.reasoning,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()