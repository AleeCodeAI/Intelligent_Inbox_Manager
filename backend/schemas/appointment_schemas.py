from pydantic import BaseModel, Field

class Appointment(BaseModel):
    email_db_id: str = Field(description="Foreign key linking to the associated email record.")
    
    event_id: str = Field(description="ID from generated calendar event")
    event_title: str = Field(description="Title of the calendar event.")
    event_start: str = Field(description="Start time of the calendar event.")
    event_end: str = Field(description="End time of the calendar event.")

    calendar_status: str = Field(description="Status of the calendar event (e.g., confirmed, error).")
    confirmation_email_status: str = Field(description="Status of the confirmation email (e.g., success, failed).")

class DeleteAppointment(BaseModel):
    gmail_id: str = Field(description="Foreign key linking to the associated email record.")
    event_id: str = Field(description="ID from generated calendar event")