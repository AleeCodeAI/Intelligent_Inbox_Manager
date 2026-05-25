from database.session import SessionLocal
from database.models.processing import EmailProcessing
from schemas import EmailProcessed


def insert_processing(gmail_id: str, data: EmailProcessed):
    db = SessionLocal()
    try:
        record = EmailProcessing(
            email_processing_id=f"proc_{gmail_id}",
            gmail_id=gmail_id,
            classification=data.result.classification,
            confidence=data.result.confidence,
            reasoning=data.result.reasoning,
            success=data.success,
            processed_date=data.processed_date,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()