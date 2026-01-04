
from pydantic import BaseModel, Field
from typing import Optional
# --------------------------
# Import your DB logic
# --------------------------
from nonbusiness_agent_database import create_db, insert_email, CleanEmailData

from typing import List

class NonBusiness(BaseModel):
    email_id: str = Field(description="Unique identifier for the email.")
    from_name: Optional[str] = None
    from_email: str = Field(description="Sender's email address.")
    subject: str = Field(description="The subject of the email.")
    message: str = Field(description="The cleaned body content of the email.")
    time: str = Field(description="Human-readable timestamp of the email.")
    classification: str = Field(description="the type of email: PERSONAL | PROMOTIONAL | INFORMATIONAL | SPAM")
    confidence: float = Field(description="confidence level for certain classification: 0.0 - 1.0")
    reasoning: str = Field(description="short explanation of why certain classification is made.")

emails: List[NonBusiness] = [
    NonBusiness(
        email_id="19b7863a40753757",
        from_name="Sarah Johnson",
        from_email="sarah.j@gmail.com",
        subject="Dinner plans this Friday?",
        message="Hey! Just wanted to check if you're free for dinner this Friday. There's a new Italian place that opened downtown. Let me know if you can make it - I can make reservations for 7 PM.",
        time="2024-03-15 14:30:00",
        classification="PERSONAL",
        confidence=0.92,
        reasoning="Personal invitation for social dinner plans with casual language"
    ),
    NonBusiness(
        email_id="19b787671b9ad02c",
        from_name="Weekly Deals Newsletter",
        from_email="offers@shoppingdeals.com",
        subject="50% OFF Spring Sale - Limited Time!",
        message="Spring into savings with our biggest sale of the season! Get 50% off all items with code SPRING50. Plus, free shipping on orders over $50. Shop now before these deals disappear!",
        time="2024-03-16 09:15:00",
        classification="PROMOTIONAL",
        confidence=0.96,
        reasoning="Marketing email promoting sales, discounts, and encouraging purchases"
    ),
    NonBusiness(
        email_id="19b7879641a137e3",
        from_name="Mike Thompson",
        from_email="mike.t@gmail.com",
        subject="Check out these photos from the trip",
        message="Finally got around to uploading the photos from our hiking trip last month. Here's the link to the album: [link]. The sunset shots from the summit turned out amazing!",
        time="2024-03-14 18:45:00",
        classification="PERSONAL",
        confidence=0.88,
        reasoning="Sharing personal photos from a trip with friend, informal communication"
    ),
    NonBusiness(
        email_id="19b7950632f713e9",
        from_name="Community Newsletter",
        from_email="news@localcommunity.org",
        subject="March Community Events Calendar",
        message="Here's what's happening in our community this March: Saturday farmers market (every week 9AM-1PM), Library book sale (March 20-22), Park cleanup day (March 25). All events are free and open to the public.",
        time="2024-03-01 08:00:00",
        classification="INFORMATIONAL",
        confidence=0.94,
        reasoning="Community event information without commercial intent or personal content"
    ),
    NonBusiness(
        email_id="19b7b51b776eece9",
        from_name="Earn Cash Fast",
        from_email="quickmoney@financialopp.com",
        subject="GET RICH QUICK - GUARANTEED $10K/MONTH",
        message="$$$ STOP WORKING FOR OTHERS $$$ Our proven system guarantees you'll make $10,000 per month from home! No experience needed. Click here to unlock the secret wealthy people don't want you to know! LIMITED TIME OFFER!",
        time="2024-03-17 23:10:00",
        classification="SPAM",
        confidence=0.99,
        reasoning="Typical spam characteristics: excessive punctuation, unrealistic claims, urgent language, get-rich-quick scheme"
    )
]

def seed_nonbusiness_emails():
    for email in emails:
        insert_email(email)

if __name__ == "__main__":
    create_db()
    seed_nonbusiness_emails()
