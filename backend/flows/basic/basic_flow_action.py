from utils.color import Logger
from utils.send_email import send_to_n8n
from utils.template import render_email
from schemas import BasicAction as basic_action
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

class BasicFlowAction(Logger):
    name: str = "BasicFlowAction"
    color: str = Logger.TURQUOISE

    def run(self, basic_action: basic_action):
        self.log(f"Executing action for email ID: {basic_action.gmail_id} from sender: {basic_action.sender_name}")

        try:
            self.log(f"Rendering manual response for email ID: {basic_action.gmail_id}")
            html_body = render_email(
                recipient_name=basic_action.sender_name, # the email will be received by the sender, so we use their name as recipient_name
                body=basic_action.manual_response
                )

            self.log(f"Sending manual response for email ID: {basic_action.gmail_id}")
            result = send_to_n8n(
                {
                    "id": basic_action.gmail_id,
                    "body": html_body,
                    "email_type": "BASIC"
                }
            )
            self.log(f"Manual response sent with status: {result['status']} for email ID: {result['emailId']}")
            return result

        except Exception as e:
            self.log(f"Error rendering manual response for email ID: {basic_action.gmail_id} - {str(e)}")
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    action = BasicFlowAction()
    gmail_id = input("Enter Gmail ID: ") # manually input the gmail_id for testing purposes
    test_action = basic_action(
        gmail_id=gmail_id,
        sender_name="John Doe",
        manual_response="I am currently unavailable. I will get back to you as soon as possible."
    )
    action.run(test_action)