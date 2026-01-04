import sqlite3
import logging
from pydantic import BaseModel, Field
from datetime import datetime
import os

# --------------------------
# Logging setup
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format='\033[92m%(asctime)s - %(levelname)s - %(message)s\033[0m',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("EmailDB")

# --------------------------
# SQLite Database Setup
# --------------------------
DB_FOLDER = r"D:\Projects\inbox-manager\databases"
os.makedirs(DB_FOLDER, exist_ok=True)
DB_NAME = os.path.join(DB_FOLDER, "nonbusiness_emails.db")

def create_db():
    """Create the emails table with all required columns."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        email_id TEXT PRIMARY KEY,
        from_name TEXT NOT NULL,
        from_email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        time TEXT NOT NULL,
        classification TEXT NOT NULL,
        confidence REAL NOT NULL,
        reasoning TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
    logger.info(f"Database created at '{DB_NAME}' and table 'emails' ready with all required columns.")

# --------------------------
# Pydantic model for email
# --------------------------
class CleanEmailData(BaseModel):
    email_id: str
    from_name: str
    from_email: str
    subject: str
    message: str
    time: str
    classification: str
    confidence: float
    reasoning: str

# --------------------------
# Insert Email
# --------------------------
def insert_email(email: CleanEmailData):
    """Insert a CleanEmailData instance into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO emails
    (email_id, from_name, from_email, subject, message, time, classification, confidence, reasoning)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email.email_id,
        email.from_name,
        email.from_email,
        email.subject,
        email.message,
        email.time,
        email.classification,
        email.confidence,
        email.reasoning
    ))
    conn.commit()
    conn.close()
    logger.info(f"Inserted email '{email.email_id}' with classification '{email.classification}' into database.")

# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    # Create DB
    create_db()
    print("Database and table created with all required columns.")

