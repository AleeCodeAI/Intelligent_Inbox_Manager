from pydantic import BaseModel, Field
from typing import Optional

class NonBusinessResult(BaseModel):
    nonbusiness_type: str = Field(description="The category assigned to the email.")
    confidence: Optional[float] = Field(description="The confidence score of the classification, if available.")
    reasoning: str = Field(description="A concise explanation of why this classification was chosen based on the email content.")