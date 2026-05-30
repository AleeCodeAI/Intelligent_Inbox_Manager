from sqlalchemy import Column, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database.base import Base


class EmailProcessing(Base):
    __tablename__ = "email_processing"

    email_processing_id = Column(String, primary_key=True)
    email_db_id = Column(
        String, 
        ForeignKey("emails.email_db_id", ondelete="CASCADE"), 
        nullable=False
        )

    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)

    success = Column(Boolean, nullable=False)
    processed_date = Column(String, nullable=False)
    email = relationship("Email")