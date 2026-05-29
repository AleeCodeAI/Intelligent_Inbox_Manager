from pydantic import BaseModel, Field
from typing import Optional

class Appointment(BaseModel):
    email_db_id: str = Field(description="Foreign key linking to the associated email record.")
    
    event_id: Optional[str] = Field(default=None)
    event_title: str = Field(description="Title of the calendar event.")
    event_start: str = Field(description="Start time of the calendar event.")
    event_end: str = Field(description="End time of the calendar event.")

    calendar_status: str = Field(description="Status of the calendar event (e.g., confirmed, error).")
    confirmation_email_status: str = Field(description="Status of the confirmation email (e.g., success, failed).")