import sqlite3
import os
from typing import List, Optional
from pydantic import BaseModel
from color import Agent

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
# Class: GetPriorityEmails
# --------------------------
class GetPriorityEmails(Agent):
    def __init__(self, db_path: str = r"D:\Projects\inbox-manager\databases\priority_emails.db"):
        self.name = "PriorityEmailGetter"
        self.color = self.YELLOW
        self.db_path = db_path

    def get_all_emails(self) -> List[PriorityEmailData]:
        """
        Retrieve all emails from the priority database.
        
        Returns:
            List of PriorityEmailData objects
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
            
            emails = [PriorityEmailData(**dict(row)) for row in rows]
            self.log(f"Retrieved {len(emails)} priority emails from database")
            
            return emails
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def get_email_by_id(self, email_id: str) -> Optional[PriorityEmailData]:
        """
        Retrieve a specific email by ID.
        
        Args:
            email_id: The email ID to search for
            
        Returns:
            PriorityEmailData object if found, None otherwise
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
                email = PriorityEmailData(**dict(row))
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

    def get_emails_by_sender(self, from_email: str) -> List[PriorityEmailData]:
        """
        Retrieve all emails from a specific sender.
        
        Args:
            from_email: The sender's email address
            
        Returns:
            List of PriorityEmailData objects from that sender
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
            
            emails = [PriorityEmailData(**dict(row)) for row in rows]
            self.log(f"Found {len(emails)} emails from {from_email}")
            
            return emails
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def get_emails_by_classification(self, classification: str) -> List[PriorityEmailData]:
        """
        Retrieve all emails with a specific classification.
        
        Args:
            classification: The classification type (e.g., 'APPOINTMENT', 'URGENT', 'IMPORTANT')
            
        Returns:
            List of PriorityEmailData objects with that classification
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM emails WHERE classification = ? ORDER BY time DESC",
                (classification,)
            )
            rows = cursor.fetchall()
            
            emails = [PriorityEmailData(**dict(row)) for row in rows]
            self.log(f"Found {len(emails)} emails with classification '{classification}'")
            
            return emails
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def get_appointments(self) -> List[PriorityEmailData]:
        """
        Retrieve all appointment emails.
        
        Returns:
            List of PriorityEmailData objects with APPOINTMENT classification
        """
        return self.get_emails_by_classification("APPOINTMENT")

    def get_urgent_emails(self) -> List[PriorityEmailData]:
        """
        Retrieve all urgent emails.
        
        Returns:
            List of PriorityEmailData objects with URGENT classification
        """
        return self.get_emails_by_classification("URGENT")

    def get_emails_by_confidence(self, min_confidence: float = 0.0, max_confidence: float = 1.0) -> List[PriorityEmailData]:
        """
        Retrieve emails within a confidence range.
        
        Args:
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
            max_confidence: Maximum confidence threshold (0.0 to 1.0)
            
        Returns:
            List of PriorityEmailData objects within the confidence range
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT * FROM emails 
                   WHERE confidence >= ? AND confidence <= ? 
                   ORDER BY confidence DESC, time DESC""",
                (min_confidence, max_confidence)
            )
            rows = cursor.fetchall()
            
            emails = [PriorityEmailData(**dict(row)) for row in rows]
            self.log(f"Found {len(emails)} emails with confidence between {min_confidence} and {max_confidence}")
            
            return emails
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def search_emails(self, search_term: str) -> List[PriorityEmailData]:
        """
        Search emails by subject, message, or reasoning content.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of PriorityEmailData objects matching the search
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
                   WHERE subject LIKE ? OR message LIKE ? OR reasoning LIKE ?
                   ORDER BY time DESC""",
                (search_pattern, search_pattern, search_pattern)
            )
            rows = cursor.fetchall()
            
            emails = [PriorityEmailData(**dict(row)) for row in rows]
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
            
            self.log(f"Total priority emails in database: {count}")
            return count
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()

    def get_classification_stats(self) -> dict:
        """
        Get statistics about email classifications.
        
        Returns:
            Dictionary with classification counts
        """
        if not os.path.exists(self.db_path):
            self.log(f"Error: Database file not found at {self.db_path}")
            return {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT classification, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM emails 
                GROUP BY classification
            """)
            rows = cursor.fetchall()
            
            stats = {row[0]: {"count": row[1], "avg_confidence": row[2]} for row in rows}
            self.log(f"Classification stats: {stats}")
            return stats
            
        except sqlite3.Error as e:
            self.log(f"Database error: {e}")
            return {}
        finally:
            if 'conn' in locals():
                conn.close()


# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    getter = GetPriorityEmails()
    
    # Get all emails
    all_emails = getter.get_all_emails()
    print(f"\nTotal priority emails: {len(all_emails)}")
    
    # Get classification stats
    stats = getter.get_classification_stats()
    print(f"\nClassification Stats:")
    for classification, data in stats.items():
        print(f"  {classification}: {data['count']} emails (avg confidence: {data['avg_confidence']:.2%})")
    
    # Get appointments
    appointments = getter.get_appointments()
    print(f"\nAppointments: {len(appointments)}")
    
    # Print first 3 emails
    for email in all_emails[:3]:
        print(f"\n- From: {email.from_name} ({email.from_email})")
        print(f"  Subject: {email.subject}")
        print(f"  Classification: {email.classification}")
        print(f"  Confidence: {email.confidence:.2%}")
        print(f"  Time: {email.time}")