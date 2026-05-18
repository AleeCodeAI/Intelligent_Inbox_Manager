from sqlalchemy import Column, String, Text, ForeignKey
from database.base import Base

class BasicEmailData(Base):
    __tablename__ = "basic_email_data"

    email_id = Column(String, ForeignKey("emails.id"), primary_key=True)

    rag_query = Column(Text, nullable=True)
    rag_response = Column(Text, nullable=True)