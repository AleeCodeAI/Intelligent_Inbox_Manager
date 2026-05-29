from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database.base import Base

class Appointment(Base):
    __tablename__ = "appointments"

    email_db_id = Column(String, ForeignKey("emails.email_db_id"), primary_key=True)
    
    event_id = Column(String, nullable=True)
    event_title = Column(String, nullable=False)
    event_start = Column(String, nullable=False)
    event_end = Column(String, nullable=False)
    
    calendar_status = Column(String, nullable=False)
    confirmation_email_status = Column(String, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())