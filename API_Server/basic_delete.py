import sqlite3
import os
from typing import Optional
from pydantic import BaseModel
from color import Agent
# --------------------------
# Models
# --------------------------
class CleanEmailData(BaseModel):
    email_id: str
    from_name: Optional[str] = None
    from_email: str
    subject: Optional[str] = None
    message: Optional[str] = None
    time: str

# --------------------------
# Class: DeleteBasicEmail
# --------------------------
class DeleteBasicEmail(Agent):
    def __init__(self, db_path: str = r"D:\Projects\inbox-manager\databases\basic_emails.db"):
        self.name = "EmailDeleter"
        self.color = self.GREEN
        self.db_path = db_path

    def _get_email_by_id(self, email_id: str) -> Optional[CleanEmailData]:
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
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
        self.log(f"Attempting verified deletion for ID: {email_id}")
        email_obj = self._get_email_by_id(email_id)

        if not email_obj:
            self.log(f"No record found for ID '{email_id}'. Skipping deletion.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = """
            DELETE FROM emails 
            WHERE email_id = ? AND from_name IS ? AND from_email = ? 
              AND subject IS ? AND message IS ? AND time = ?
            """
            cursor.execute(query, (
                email_obj.email_id, email_obj.from_name, email_obj.from_email,
                email_obj.subject, email_obj.message, email_obj.time
            ))
            conn.commit()

            if cursor.rowcount > 0:
                self.log(f"Success: Exact match for '{email_id}' deleted from DB.")
            else:
                self.log(f"Verification mismatch: Record '{email_id}' was not deleted.")
        except sqlite3.Error as e:
            self.log(f"Database error during deletion: {e}")
        finally:
            if conn: conn.close()

            