from database.session import SessionLocal
from database.models.processing import EmailProcessing
from schemas import EmailProcessed


def insert_processing(gmail_id: str, data: EmailProcessed):
    db = SessionLocal()
    try:
        record = EmailProcessing(
            email_processing_id=f"proc_{gmail_id}",
            gmail_id=gmail_id,
            classification=data.classification,
            confidence=data.confidence,
            reasoning=data.reasoning,
            success=data.success,
            processed_date=data.processed_date
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()