import sqlite3
import os
from typing import List, Optional
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
# Class: GetBasicEmails
# --------------------------
class GetBasicEmails(Agent):
    def __init__(self, db_path: str = r"D:\Projects\inbox-manager\databases\basic_emails.db"):
        self.name = "BasicEmailGetter"
        self.color = self.GREEN
        self.db_path = db_path

    def get_all_emails(self) -> List[CleanEmailData]:
        """
        Retrieve all emails from the basic_emails database.
        
        Returns:
            List of CleanEmailData objects
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM emails ORDER BY time DESC")
            rows = cursor.fetchall()
            
            emails = [CleanEmailData(**dict(row)) for row in rows]
            self.log(f"Retrieved {len(emails)} emails from database")
            
            return emails
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def get_email_by_id(self, email_id: str) -> Optional[CleanEmailData]:
        """
        Retrieve a specific email by ID.
        
        Args:
            email_id: The email ID to search for
            
        Returns:
            CleanEmailData object if found, None otherwise
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM emails WHERE email_id = ?", (email_id,))
            row = cursor.fetchone()
            
            if row:
                email = CleanEmailData(**dict(row))
                self.log(f"Found email with ID: {email_id}")
                return email
            else:
                self.log(f"No email found with ID: {email_id}")
                return None
                
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def get_emails_by_sender(self, from_email: str) -> List[CleanEmailData]:
        """
        Retrieve all emails from a specific sender.
        
        Args:
            from_email: The sender's email address
            
        Returns:
            List of CleanEmailData objects from that sender
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM emails WHERE from_email = ? ORDER BY time DESC",
                (from_email,)
            )
            rows = cursor.fetchall()
            
            emails = [CleanEmailData(**dict(row)) for row in rows]
            self.log(f"Found {len(emails)} emails from {from_email}")
            
            return emails
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def search_emails(self, search_term: str) -> List[CleanEmailData]:
        """
        Search emails by subject or message content.
        
        Args:
            search_term: Term to search for in subject or message
            
        Returns:
            List of CleanEmailData objects matching the search
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute(
                """SELECT * FROM emails 
                   WHERE subject LIKE ? OR message LIKE ? 
                   ORDER BY time DESC""",
                (search_pattern, search_pattern)
            )
            rows = cursor.fetchall()
            
            emails = [CleanEmailData(**dict(row)) for row in rows]
            self.log(f"Found {len(emails)} emails matching '{search_term}'")
            
            return emails
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def get_email_count(self) -> int:
        """
        Get the total count of emails in the database.
        
        Returns:
            Total number of emails
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return 0

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM emails")
            count = cursor.fetchone()[0]
            
            self.log(f"Total emails in database: {count}")
            return count
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()


# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    getter = GetBasicEmails()
    
    # Get all emails
    all_emails = getter.get_all_emails()
    print(f"\nTotal emails: {len(all_emails)}")
    
    for email in all_emails[:5]:  # Print first 5
        print(f"- From: {email.from_name} ({email.from_email})")
        print(f"  Subject: {email.subject}")
        print(f"  Time: {email.time}")
        print()
    
    # Get email count
    count = getter.get_email_count()
    print(f"Email count: {count}")