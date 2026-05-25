from pydantic import BaseModel, Field
from datetime import datetime


class ExecutorResult(BaseModel):
    classification: str = Field(description="Classification of email: Basic | Priority | NonBusiness")
    confidence: float = Field(description="Confidence score for the classification, between 0 and 1")
    reasoning: str = Field(description="Explanation of the classification decision")

class EmailProcessed(BaseModel):

    gmail_id: str = Field(description="The ID of the original email that was processed")
    result: ExecutorResult = Field(description="The result of processing the email, including classification, confidence, and reasoning")
    processed_date: datetime = Field(description="Date when the email was processed")
    success: bool = Field(description="Indicates if the email was successfully processed")

