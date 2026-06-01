from pydantic import BaseModel, Field
from typing import Optional, Literal

# =========================================================
# priority_flow.py
# =========================================================
class PriorityResult(BaseModel):
    priority_type: Literal["SENSITIVE", "HIGH_VALUE", "CLIENT_COMMUNICATION", "APPOINTMENT"] = Field(description="The category assigned to the email.")
    confidence: float = Field(ge=0.0, le=1.0, description="The confidence score of the classification, if available.")
    reasoning: str = Field(description="A concise explanation of why this classification was chosen based on the email content.")


# =========================================================
# priority_action.py
# =========================================================
class CalendarEventDetails(BaseModel):
    title: str = Field(description="Title of the calendar event.")
    start: str = Field(description="Start date and time of the event.")
    end: str = Field(description="End date and time of the event.")

class PriorityAction(BaseModel):
    gmail_id: str = Field(description="Gmail unique message ID for threading/replying.")
    sender_name: str = Field(description="Name of the email sender.")
    priority_type: str = Field(description="Category: 'legal', 'appointment', 'financial', etc.")
    manual_response: str = Field(description="The human-written reply body.")
    calendar_details: Optional[CalendarEventDetails] = Field(description="If the action involves scheduling, the proposed event details.")