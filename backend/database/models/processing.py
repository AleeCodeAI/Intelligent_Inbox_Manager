from sqlalchemy import Column, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database.base import Base

class EmailProcessing(Base):
    __tablename__ = "email_processing"

    id = Column(String, primary_key=True)
    email_id = Column(String, ForeignKey("emails.id"), nullable=False)

    classification = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)

    success = Column(Boolean, nullable=False) 
    processed_date = Column(String, nullable=True)

    email = relationship("Email")
