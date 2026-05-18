from sqlalchemy import Column, String, ForeignKey, Boolean
from database.base import Base

class PriorityEmailData(Base):
    __tablename__ = "priority_email_data"

    email_id = Column(String, ForeignKey("emails.id"), primary_key=True)

    priority_type = Column(String, nullable=True)
    reviewed = Column(Boolean, default=False) # reviewed here means human answered this email and confirmed the priority