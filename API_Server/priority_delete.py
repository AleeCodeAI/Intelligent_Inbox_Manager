import sqlite3
import os
from typing import Optional
from color import Agent
from pydantic import BaseModel

# --------------------------
# Models
# --------------------------
class PriorityEmailData(BaseModel):
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
# Class: DeletePriorityEmail
# --------------------------
class DeletePriorityEmail(Agent):
    def __init__(self, db_path: str = r"D:\Projects\inbox-manager\databases\priority_emails.db"):
        self.name = "PriorityDeleter"
        self.color = self.YELLOW
        self.db_path = db_path

    def _get_email_by_id(self, email_id: str) -> Optional[PriorityEmailData]:
        """Fetches the full row from the priority DB."""
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database not found at {self.db_path}")
            return None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE email_id = ?", (email_id,))
            row = cursor.fetchone()
            return PriorityEmailData(**dict(row)) if row else None
        except sqlite3.Error as e:
            self.log(f"Fetch Error: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def delete_email(self, email_id: str):
        """Verifies core fields before deleting."""
        self.log(f"Starting verified deletion for Priority ID: {email_id}")
        email_obj = self._get_email_by_id(email_id)

        if not email_obj:
            self.log(f"Notice: ID '{email_id}' not found. Skipping.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Flexible match: ignores confidence and reasoning
            query = """
            DELETE FROM emails 
            WHERE email_id = ? AND from_name = ? AND from_email = ? 
              AND subject = ? AND message = ? AND time = ? AND classification = ?
            """
            params = (
                email_obj.email_id, email_obj.from_name, email_obj.from_email,
                email_obj.subject, email_obj.message, email_obj.time, 
                email_obj.classification
            )
            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount > 0:
                self.log(f"Success: Verified Priority Email '{email_id}' deleted.")
            else:
                self.log(f"Mismatch: Row exists but fields didn't match verification.")
        finally:
            if 'conn' in locals(): conn.close()