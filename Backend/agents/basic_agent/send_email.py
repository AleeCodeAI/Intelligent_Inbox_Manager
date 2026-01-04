import requests

def send_to_n8n(data):
    """
    Sends a Python dictionary as JSON to the specified n8n webhook.
    Returns a clean dictionary with 'status' and 'emailId'.
    """
    url = "http://localhost:5678/webhook/b2a962e2-927f-40d9-8e60-ccf4241c3228"
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        
        try:
            result = response.json()
        except ValueError:
            return {"status": "failed", "emailId": None, "raw_response": response.text}

        if isinstance(result, dict):
            # Look for nested 'data' key
            for key, val in result.items():
                if isinstance(val, dict) and "data" in val and isinstance(val["data"], list) and val["data"]:
                    first_item = val["data"][0]
                    status = first_item.get("status")
                    emailId = first_item.get("emailId")
                    return {"status": status, "emailId": emailId}
            
            # Otherwise check top-level status/emailId
            if "status" in result and "emailId" in result:
                return {"status": result["status"], "emailId": result["emailId"]}

        # fallback
        return {"status": "failed", "emailId": None, "raw_response": result}

    except requests.Timeout:
        return {"status": "failed", "emailId": None, "error": "n8n request timed out"}

    except requests.RequestException as e:
        return {"status": "failed", "emailId": None, "error": str(e)}


if __name__ == "__main__":
    email_payload = {
        "id": "19b640e16056d87c",
        "body": "Hello,\n\nJust a quick update: the task has been completed successfully.\n\nBest regards,\nAlee",
    }
    
    result = send_to_n8n(email_payload)

    print("Clean Response from n8n:")
    print(result)
