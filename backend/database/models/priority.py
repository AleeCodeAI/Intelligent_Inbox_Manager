from sqlalchemy import Column, String, ForeignKey, Boolean
from database.base import Base

class PriorityEmailData(Base):
    __tablename__ = "priority_email_data"

    email_db_id = Column(String, ForeignKey("emails.email_db_id"), primary_key=True)

    priority_type = Column(String, nullable=True)
    reviewed = Column(Boolean, default=False) # reviewed here means human answered this email and confirmed the priority