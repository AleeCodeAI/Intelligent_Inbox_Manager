from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Float
from database.base import Base


class NonBusinessEmailData(Base):
    __tablename__ = "nonbusiness_email_data"

    email_db_id = Column(
        String, 
        ForeignKey("emails.email_db_id", ondelete="CASCADE"), 
        primary_key=True
        )

    nonbusiness_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)

    reviewed = Column(Boolean, default=False)