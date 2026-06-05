from utils.send_email import send_to_n8n
from utils.color import Logger
from utils.template import render_email
from schemas import NonBusinessAction as nonbusiness_action
from database import mark_nonbusiness_reviewed, get_email_by_gmail_id

class NonBusinessAction(Logger):
    name: str = "NonBusinessAction"
    color: str = Logger.GOLD

    def run(self, nonbusiness_action: nonbusiness_action):
        self.log(f"Executing action for email ID: {nonbusiness_action.gmail_id} with non-business type: {nonbusiness_action.nonbusiness_type}")

        self.log("Fetching email record from database")
        email_record = get_email_by_gmail_id(nonbusiness_action.gmail_id)

        try:
            self.log(f"Rendering manual response for email ID: {nonbusiness_action.gmail_id}")
            html_body = render_email(
                recipient_name=nonbusiness_action.sender_name, # the email will be received by the sender, so we use their name as recipient_name
                body=nonbusiness_action.manual_response
                )

            self.log(f"Sending manual response for email ID: {nonbusiness_action.gmail_id}")
            result = send_to_n8n(
                {
                    "id": nonbusiness_action.gmail_id,
                    "body": html_body,
                    "email_type": "NONBUSINESS"
                }
            )
            self.log(f"Manual response sent with status: {result['status']} for email ID: {result['emailId']}")

            self.log("Marking the reviewed as TRUE in database")
            mark_nonbusiness_reviewed(email_record.email_db_id)

            return result

        except Exception as e:
            self.log(f"Error rendering manual response for email ID: {nonbusiness_action.gmail_id} - {str(e)}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    action = NonBusinessAction()
    gmail_id = input("Enter Gmail ID: ") # manually input the gmail_id for testing purposes
    test_action = nonbusiness_action(
        gmail_id=gmail_id,
        sender_name="John Doe",
        manual_response="I am currently unavailable. I will get back to you as soon as possible.",
        nonbusiness_type="PERSONAL"
    )
    action.run(test_action)