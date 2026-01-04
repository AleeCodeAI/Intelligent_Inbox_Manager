import sqlite3
import os
from typing import Optional
from color import Agent
from pydantic import BaseModel

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

class DeleteNonBusinessEmail(Agent):
    def __init__(self, db_path: str = r"D:\Projects\inbox-manager\databases\nonbusiness_emails.db"):
        self.name = "NonBusinessDeleter"
        self.color = self.RED
        self.db_path = db_path

    def _get_email_by_id(self, email_id: str) -> Optional[CleanEmailData]:
        """Fetches the full row from the DB."""
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database not found at {self.db_path}")
            return None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE email_id = ?", (email_id,))
            row = cursor.fetchone()
            return CleanEmailData(**dict(row)) if row else None
        finally:
            if 'conn' in locals(): conn.close()

    def delete_email(self, email_id: str):
        """Fetches email object first, then deletes it."""
        self.log(f"Searching for ID {email_id} for deletion...")
        email_obj = self._get_email_by_id(email_id)

        if not email_obj:
            self.log(f"Notice: ID '{email_id}' not found. Nothing to delete.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Deleting by verified ID
            cursor.execute("DELETE FROM emails WHERE email_id = ?", (email_obj.email_id,))
            conn.commit()

            if cursor.rowcount > 0:
                self.log(f"Success: Email '{email_id}' deleted from non-business database.")
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
        finally:
            if 'conn' in locals(): conn.close()