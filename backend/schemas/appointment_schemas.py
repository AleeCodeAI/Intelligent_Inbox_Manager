from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Appointment(BaseModel):
    appointment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email_db_id: str = Field(description="Foreign key linking to the associated email record.")
    
    event_id: Optional[str] = Field(default=None, description="Google Calendar event ID returned by n8n.")
    event_title: str = Field(description="Title of the calendar event.")
    event_start: str = Field(description="Start date and time of the event.")
    event_end: str = Field(description="End date and time of the event.")
    
    calendar_status: str = Field(description="Status of the calendar event (e.g., confirmed, error).")
    confirmation_email_status: str = Field(description="Status of the confirmation email (e.g., success, failed).")
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())