from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from database.base import Base

class NonBusinessEmailData(Base):
    __tablename__ = "nonbusiness_email_data"

    email_id = Column(String, ForeignKey("emails.id"), primary_key=True)

    reason = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    reviewed = Column(Boolean, default=False) # reviewed here means human answered this email and confirmed the priority