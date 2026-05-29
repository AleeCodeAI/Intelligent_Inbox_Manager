from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database.base import Base

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(String, primary_key=True, index=True)
    email_db_id = Column(String, ForeignKey("emails.email_db_id"), nullable=False)
    
    event_id = Column(String, nullable=True)  # Google Calendar event ID returned by n8n
    event_title = Column(String, nullable=False)
    event_start = Column(String, nullable=False)
    event_end = Column(String, nullable=False)
    
    calendar_status = Column(String, nullable=False)  # confirmed, error, etc.
    confirmation_email_status = Column(String, nullable=False)  # success, failed, etc.
    
    created_at = Column(DateTime, server_default=func.now())