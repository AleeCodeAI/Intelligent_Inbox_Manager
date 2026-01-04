import requests
from typing import Dict, Any
from color import Agent 

# --------------------------
# Class: SendBasicEmail
# --------------------------
class SendBasicEmail(Agent):
    def __init__(self):
        self.name = "BasicEmailSender"
        self.color = self.GREEN
        self.webhook_url = "http://localhost:5678/webhook/b2a962e2-927f-40d9-8e60-ccf4241c3228"

    def send_email(self, email_id: str, crafted_message: str) -> Dict[str, Any]:
        """
        Directly sends the provided email_id and crafted_message to n8n.
        No database lookup performed.
        """
        self.log(f"Preparing to send crafted email for ID: {email_id}")
        
        payload = {
            "id": email_id, 
            "body": crafted_message
        }

        try:
            self.log(f"Sending payload to n8n webhook...")
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Result parsing logic
            final_res = {"status": "failed", "emailId": None}
            if isinstance(result, dict):
                # Check for nested n8n data structure
                for key, val in result.items():
                    if isinstance(val, dict) and "data" in val and val["data"]:
                        first = val["data"][0]
                        final_res = {"status": first.get("status"), "emailId": first.get("emailId")}
                
                # Check top-level keys
                if "status" in result and "emailId" in result:
                    final_res = {"status": result["status"], "emailId": result["emailId"]}

            self.log(f"Successfully sent. n8n Status: {final_res.get('status')}")
            return final_res

        except Exception as e:
            self.log(f"Request failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    sender = SendBasicEmail()
    # Direct execution with provided parameters
    sender.send_email(
        email_id="19b640e16056d87c", 
        crafted_message="This is a direct crafted message sent without DB retrieval."
    )