import sqlite3
import os
from typing import Optional
from color import Agent
from pydantic import BaseModel

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
# Class: DeleteSchedulerEmail
# --------------------------
class DeleteSchedulerEmail(Agent):
    def __init__(self, db_path: str = r"D:\Projects\inbox-manager\databases\scheduler_emails.db"):
        self.name = "SchedulerDeleter"
        self.color = self.BLUE
        self.db_path = db_path

    def _get_email_by_id(self, email_id: str) -> Optional[CleanEmailData]:
        """Fetches the full row from the scheduler DB."""
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
        except sqlite3.Error as e:
            self.log(f"Database error during fetch: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def delete_email(self, email_id: str):
        """Extracts the object first, then deletes it if an exact match is found."""
        self.log(f"Verification requested for deletion of ID: {email_id}")
        email_obj = self._get_email_by_id(email_id)

        if not email_obj:
            self.log(f"Notice: No email found with ID '{email_id}'.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Exact match query for all columns
            query = """
            DELETE FROM emails 
            WHERE email_id = ? 
              AND from_name IS ? 
              AND from_email = ? 
              AND subject IS ? 
              AND message IS ? 
              AND time = ?
            """
            params = (
                email_obj.email_id, email_obj.from_name, email_obj.from_email,
                email_obj.subject, email_obj.message, email_obj.time
            )

            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount > 0:
                self.log(f"Success: Verified scheduler email '{email_id}' deleted.")
            else:
                self.log(f"Notice: No matching object found; no row was deleted.")
        except sqlite3.Error as e:
            self.log(f"Database error during deletion: {e}")
        finally:
            if 'conn' in locals(): conn.close()