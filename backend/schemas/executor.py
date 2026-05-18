from pydantic import BaseModel, Field
from typing import Optional


class EmailProcessed(BaseModel):

    inbound_email_id: str = Field(description="The ID of the original email that was processed")
    classification: Optional[str] = Field(description="Classification of email: Basic | Priority | NonBusiness")
    confidence: Optional[float] = Field(description="Confidence score for the classification, between 0 and 1")
    reasoning: Optional[str] = Field(description="Explanation of the classification decision")
    processed_date: Optional[str] = Field(default=None, description="Date when the email was processed")
    success: bool = Field(description="Indicates if the email was successfully processed")
