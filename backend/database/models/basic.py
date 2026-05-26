from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON
from database.base import Base

class BasicEmailData(Base):
    __tablename__ = "basic_email_data"

    email_db_id = Column(String, ForeignKey("emails.email_db_id"), primary_key=True)

    rag_answer = Column(Text, nullable=True)
    citations = Column(JSON, nullable=True)

    rag_status = Column(String, nullable=False)  # "success" | "failed"
    failure_reason = Column(Text, nullable=True)

    needs_manual_reply = Column(Boolean, default=False)
    reviewed = Column(Boolean, default=False) # reviewed here means human answered this email upon rag failure or if the rag successfully replied!