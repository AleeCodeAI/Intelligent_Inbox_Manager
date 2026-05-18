from database.session import SessionLocal
from database.models.basic import BasicEmailData


def insert_basic(email_id: str, rag_query: str, rag_response: str):
    db = SessionLocal()
    try:
        record = BasicEmailData(
            email_id=email_id,
            rag_query=rag_query,
            rag_response=rag_response,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()