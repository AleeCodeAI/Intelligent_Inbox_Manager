import sqlite3
import logging
from pydantic import BaseModel, Field
from typing import Optional
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
DB_NAME = os.path.join(DB_FOLDER, "basic_emails.db")

def create_db():
    """Create the emails table with only the CleanEmailData columns."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        email_id TEXT PRIMARY KEY,
        from_name TEXT,
        from_email TEXT NOT NULL,
        subject TEXT,
        message TEXT,
        time TEXT
    )
    """)
    conn.commit()
    conn.close()
    logger.info(f"Database created at '{DB_NAME}' and table 'emails' ready.")

# --------------------------
# Insert Email
# --------------------------
def insert_email(email):
    """Insert a CleanEmailData instance into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO emails
    (email_id, from_name, from_email, subject, message, time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        email.email_id,
        email.from_name,
        email.from_email,
        email.subject,
        email.message,
        email.time
    ))
    conn.commit()
    conn.close()
    logger.info(f"Inserted email '{email.email_id}' into database.")

# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    # Create DB
    create_db()
    print("Database and table created.")
