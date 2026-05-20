from pydantic import BaseModel
from typing import Optional
from .agentic_rag_schemas import Citation

class BasicLLMInput(BaseModel):
    sender_name: Optional[str] = None
    sender_email: str
    message: str
    rag_answer: str
    citations: list[Citation]

class BasicEmailResponse(BaseModel):
    body: str  # plain text — template.py wraps this in HTML