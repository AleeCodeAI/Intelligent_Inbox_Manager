from utils.mark_calendar import mark_calendar
from utils.color import Logger
from utils.send_email import send_to_n8n
from utils.template import render_email
from utils.appointment_confirmation_template import render_appointment_confirmation

from schemas import PriorityAction as priotiy_action, CalendarEventDetails

class PriorityAction(Logger):
    name: str = "PriorityAction"
    color: str = Logger.PINK

    def run(self, priority_email: priotiy_action):
        self.log(f"Executing action for email ID: {priority_email.gmail_id} with priority type: {priority_email.priority_type}")

        try:
            if priority_email.priority_type.upper() == "APPOINTMENT" and priority_email.calendar_details:
                calendar_details: CalendarEventDetails = priority_email.calendar_details
                result = mark_calendar(
                    title=calendar_details.title,
                    start=calendar_details.start,
                    end=calendar_details.end
                )
                self.log(f"Calendar event created for ID: {result.get('id')} with status: {result.get('status')}")
                self.log(f"Rendering appointment confirmation email for email ID: {priority_email.gmail_id}")
                html_body = render_appointment_confirmation(
                    recipient_name=priority_email.sender_name, # the email will be received by the sender, so we use their name as recipient_name
                    title=calendar_details.title,
                    start=calendar_details.start,
                    end=calendar_details.end
                )
                self.log(f"Sending appointment confirmation email for email ID: {priority_email.gmail_id}")
                result = send_to_n8n({
                    "id": priority_email.gmail_id,
                    "body": html_body,
                    "email_type": "PRIORITY"
                })
                self.log(f"Appointment confirmation email sent with status: {result['status']} for email ID: {result['emailId']}")

            self.log(f"Rendering manual response for email ID: {priority_email.gmail_id}")
            html_body = render_email(
                recipient_name=priority_email.sender_name, # the email will be received by the sender, so we use their name as recipient_name
                body=priority_email.manual_response
                )

            self.log(f"Sending manual response for email ID: {priority_email.gmail_id}")
            result = send_to_n8n({
                "id": priority_email.gmail_id,
                "body": html_body,
                "email_type": "PRIORITY"
            })
            self.log(f"Email sent with status: {result['status']} for email ID: {result['emailId']}")
            return result

        except Exception as e:
            self.log(f"Error executing action: {str(e)}", level="error")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Example usage
    action = PriorityAction()
    test_email = priotiy_action(
        gmail_id="19e65562885fc360",
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