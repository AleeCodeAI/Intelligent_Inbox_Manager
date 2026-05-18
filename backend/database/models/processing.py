from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class EmailProcessing(Base):
    __tablename__ = "email_processing"

    id = Column(String, primary_key=True)
    email_id = Column(String, ForeignKey("emails.id"), nullable=False)

    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    reasoning = Column(String, nullable=True)

    email = relationship("Email")