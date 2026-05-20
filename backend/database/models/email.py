from sqlalchemy import Column, String, Text
from database.base import Base

class Email(Base):
    __tablename__ = "emails"

    email_db_id = Column(String, primary_key=True, index=True)
    gmail_id = Column(String, nullable=False, index=True)
    thread_id = Column(String, nullable=True)
    sender_name = Column(String, nullable=True)
    sender_email = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=True)