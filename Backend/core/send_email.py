import requests

def send_to_n8n(data):
    """
    Sends a Python dictionary as JSON to the specified n8n webhook.
    Args:
        data (dict): The data to send to n8n.
    Returns:
        dict: Response from the n8n webhook (parsed as JSON if possible).
    """
    url = "http://localhost:5678/webhook/98268ad9-e026-44f4-9612-a5030f1ef890"
    
    try:
        data = {"subject": data['subject'], "body": data['body']}
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raises an error if the request failed
        # Try to parse JSON response, fallback to text
        try:
            return response.json()
        except ValueError:
            return {"response_text": response.text}
        
    except requests.RequestException as e:
        return {"error": str(e)}