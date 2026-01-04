import requests
from typing import Dict, Any
from color import Agent

# --------------------------
# Class: NonBusinessSendEmail
# --------------------------
class NonBusinessSendEmail(Agent):
    def __init__(self):
        self.name = "NonBusinessSendEmail"
        self.color = self.RED
        # Specific webhook for non-business emails
        self.webhook_url = "http://localhost:5678/webhook/5ff54f86-9344-4dcf-b5f0-e1e6c637a5e6"

    def send_email(self, email_id: str, crafted_message: str) -> Dict[str, Any]:
        """
        Directly sends the provided email_id and crafted_message to n8n.
        """
        self.log(f"Initiating direct send for Email ID: {email_id}")
        
        # Prepare payload with the custom crafted message
        payload = {
            "id": email_id,
            "body": crafted_message
        }

        # Send to n8n
        try:
            self.log("Sending payload to non-business n8n webhook...")
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            try:
                result = response.json()
            except ValueError:
                self.log("Received non-JSON response from n8n.")
                return {"status": "failed", "emailId": None, "raw_response": response.text}

            # Handle response parsing
            final_res = {"status": "failed", "emailId": None}
            if isinstance(result, dict):
                # Check for nested n8n data structure
                for key, val in result.items():
                    if isinstance(val, dict) and "data" in val and isinstance(val["data"], list) and val["data"]:
                        first_item = val["data"][0]
                        final_res = {
                            "status": first_item.get("status"), 
                            "emailId": first_item.get("emailId")
                        }
                
                # Check top-level keys
                if "status" in result and "emailId" in result:
                    final_res = {"status": result["status"], "emailId": result["emailId"]}

            self.log(f"n8n result: Status={final_res.get('status')} ID={final_res.get("emailId")}")
            return final_res

        except requests.Timeout:
            self.log("Error: n8n request timed out.")
            return {"status": "failed", "emailId": None, "error": "n8n request timed out"}
        except requests.RequestException as e:
            self.log(f"HTTP Error: {str(e)}")
            return {"status": "failed", "emailId": None, "error": str(e)}

# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    sender = NonBusinessSendEmail()
    # Sending direct ID and crafted message
    response = sender.send_email(
        email_id="19b640e16056d87c", 
        crafted_message="This is a tailored non-business response."
    )
    print(response)