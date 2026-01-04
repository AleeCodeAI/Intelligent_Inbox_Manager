import requests
from typing import Dict, Any
from color import Agent

# --------------------------
# Class: SchedulerSendEmail
# --------------------------
class SchedulerSendEmail(Agent):
    def __init__(self):
        self.name = "SchedulerSendEmail"
        self.color = self.BLUE
        # Specific webhook for scheduler emails
        self.webhook_url = "http://localhost:5678/webhook/940d1ba2-2624-4de7-a320-18bd4fa525b4"

    def send_email(self, email_id: str, crafted_message: str) -> Dict[str, Any]:
        """
        Directly sends the provided email_id and crafted_message to n8n.
        No database lookup performed.
        """
        self.log(f"Initiating direct scheduler send for ID: {email_id}")
        
        payload = {
            "id": email_id, 
            "body": crafted_message
        }

        try:
            self.log("Sending payload to scheduler n8n webhook...")
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Result parsing logic
            final_res = {"status": "failed", "emailId": None}
            if isinstance(result, dict):
                # Handle nested n8n 'data' structure
                for key, val in result.items():
                    if isinstance(val, dict) and "data" in val and val["data"]:
                        first = val["data"][0]
                        final_res = {
                            "status": first.get("status"), 
                            "emailId": first.get("emailId")
                        }
                
                # Handle top-level keys
                if "status" in result:
                    final_res["status"] = result["status"]
                    if "emailId" in result:
                        final_res["emailId"] = result["emailId"]

            self.log(f"n8n Success: {final_res.get('status')}")
            return final_res

        except Exception as e:
            self.log(f"n8n request failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    sender = SchedulerSendEmail()
    # Sending direct ID and crafted message
    response = sender.send_email(
        email_id="19b640e16056d87c", 
        crafted_message="I have scheduled our call for next Tuesday. Talk soon!"
    )
    print(response)