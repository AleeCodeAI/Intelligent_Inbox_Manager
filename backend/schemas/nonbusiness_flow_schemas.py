from pydantic import BaseModel, Field
from typing import Optional

#============================================
# non_business_flow.py
#============================================
class NonBusinessResult(BaseModel):
    nonbusiness_type: str = Field(description="The category assigned to the email.")
    confidence: Optional[float] = Field(description="The confidence score of the classification, if available.")
    reasoning: str = Field(description="A concise explanation of why this classification was chosen based on the email content.")

#============================================
# non_business_action.py
#============================================
class NonBusinessAction(BaseModel):
    gmail_id: str = Field(description="The unique identifier of the email in Gmail.")
    sender_name: str = Field(description="Name of the email sender.")
    manual_response: str = Field(description="The manual response to be sent to the sender.")
    nonbusiness_type: str = Field(description="The non business category assigned to the email.")