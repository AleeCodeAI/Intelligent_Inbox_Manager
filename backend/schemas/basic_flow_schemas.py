from pydantic import BaseModel, Field
from typing import Optional
from .agentic_rag_schemas import Citation

# ===================================================================
# basic_flow.py schemas
# ===================================================================
class BasicLLMInput(BaseModel):
    sender_name: Optional[str] = None
    sender_email: str
    message: str
    rag_answer: str
    citations: list[Citation]

class BasicEmailResponse(BaseModel):
    body: str  # plain text — template.py wraps this in HTML

# ===================================================================
# basic_flow.py schemas
# ===================================================================
class BasicAction(BaseModel):
    gmail_id: str = Field(description="The unique identifier of the email in Gmail.")
    sender_name: str = Field(description="Name of the email sender.")
    manual_response: str = Field(description="The manual response to be sent to the sender.")