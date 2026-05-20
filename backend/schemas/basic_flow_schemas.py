from pydantic import BaseModel
from typing import Optional


class AgentInput(BaseModel):
    sender_name: Optional[str] = None
    sender_email: str
    message: str
    rag_reply: str


class EmailResponse(BaseModel):
    body: str  # plain text — template.py wraps this in HTML