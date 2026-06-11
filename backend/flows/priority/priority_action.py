from utils.mark_calendar import mark_calendar
from utils.color import Logger
from utils.send_email import send_to_n8n
from utils.template import render_email
from utils.appointment_confirmation_template import render_appointment_confirmation
from database import insert_appointment, get_email_by_gmail_id, mark_priority_reviewed
from schemas import Appointment

from schemas import PriorityAction as priotiy_action, CalendarEventDetails

class PriorityAction(Logger):
    name: str = "PriorityAction"
    color: str = Logger.PINK

    def run(self, priority_action: priotiy_action):
        self.log(f"Executing action for email ID: {priority_action.gmail_id} with priority type: {priority_action.priority_type}")

        self.log("Fetching email record from database")
        email_record = get_email_by_gmail_id(priority_action.gmail_id)

        try:
            # -------------------------------------------------------------------
            # Appointment Handling
            # -------------------------------------------------------------------

            if priority_action.calendar_details:

                self.log(f"Step 1: Marking calendar for email ID: {priority_action.gmail_id} with event title: {priority_action.calendar_details.title}")
                calendar_details: CalendarEventDetails = priority_action.calendar_details
                calendar_result = mark_calendar(
                    title=calendar_details.title,
                    start=calendar_details.start,
                    end=calendar_details.end
                )
                self.log(f"Calendar event created for ID: {calendar_result.get('id')} with status: {calendar_result.get('status')}")

                self.log(f"Step 2: Rendering appointment confirmation email for email ID: {priority_action.gmail_id}")
                html_body = render_appointment_confirmation(
                    recipient_name=priority_action.sender_name, # the email will be received by the sender, so we use their name as recipient_name
                    title=calendar_details.title,
                    start=calendar_details.start,
                    end=calendar_details.end
                )
                self.log(f"Step 3: Sending appointment confirmation email for email ID: {priority_action.gmail_id}")
                email_result = send_to_n8n({
                    "id": priority_action.gmail_id,
                    "body": html_body,
                    "email_type": "PRIORITY"
                })
                self.log(f"Appointment confirmation email sent with status: {email_result['status']} for email ID: {email_result['emailId']}")

                self.log(f"Step 4: Inserting appointment record into database for email ID: {priority_action.gmail_id}")

                try:
                    if not email_record:
                        self.log(f"Email record not found for gmail_id: {priority_action.gmail_id}")
                    else:
                        appointment = Appointment(
                            email_db_id=email_record.email_db_id,
                            event_id=calendar_result.get("id"),
                            event_title=calendar_details.title,
                            event_start=calendar_details.start,
                            event_end=calendar_details.end,
                            calendar_status=calendar_result.get("status"),
                            confirmation_email_status=email_result.get("status")
                        )
                        insert_appointment(appointment)
                        self.log(f"Appointment record inserted for email ID: {priority_action.gmail_id}")
                except Exception as db_error:
                    self.log(f"Failed to insert appointment record: {str(db_error)}")

            # -------------------------------------------------------------------
            # Manual Response Handling
            # -------------------------------------------------------------------

            self.log(f"Rendering manual response for email ID: {priority_action.gmail_id}")
            html_body = render_email(
                recipient_name=priority_action.sender_name, # the email will be received by the sender, so we use their name as recipient_name
                body=priority_action.manual_response
                )

            self.log(f"Sending manual response for email ID: {priority_action.gmail_id}")
            result = send_to_n8n({
                "id": priority_action.gmail_id,
                "body": html_body,
                "email_type": "PRIORITY"
            })
            self.log(f"Email sent with status: {result['status']} for email ID: {result['emailId']}")

            self.log("Marking the reviewed as TRUE in database")
            mark_priority_reviewed(email_record.email_db_id)
            return result

        except Exception as e:
            self.log(f"Error executing action: {str(e)}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    action = PriorityAction()
    gmail_id = input("Enter Gmail ID: ") # manually input the gmail_id for testing purposes
    test_email = priotiy_action(
        gmail_id=gmail_id,
        sender_name="John Doe",
        priority_type="APPOINTMENT",
        manual_response="Thank you for reaching out. I've scheduled a meeting for us to discuss this further. Please let me know if the proposed time works for you or if you'd like to suggest an alternative.",
        calendar_details=CalendarEventDetails(
            title="Meeting with John",
            start="2026-05-29T08:00:00+05:00",
            end="2026-05-29T09:00:00+05:00"
        )
    )
    action.run(test_email)