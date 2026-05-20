from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class InboundEmail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="Unique email identifier")
    thread_id: Optional[str] = Field(default=None, alias="threadId", description="Thread identifier for reply context")
    sender_name: Optional[str] = Field(default=None, alias="senderName", description="Display name of the sender")
    sender_email: str = Field(alias="senderEmail", description="Sender email address")
    subject: str = Field(description="Email subject line")
    date: Optional[str] = Field(default=None, description="Email received date")
    body: Optional[str] = Field(default=None, description="Full email body, None if no content could be extracted")

class InboundEmailBatch(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(description="Total number of new emails returned")
    emails: list[InboundEmail] = Field(description="List of new unread emails")