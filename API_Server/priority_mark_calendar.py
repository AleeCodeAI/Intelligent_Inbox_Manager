import requests

def mark_calendar(title, start, end):
    """
    Sends calendar event data to n8n webhook and returns status and id.
    
    Args:
        title (str): Event title
        start (str): Event start time
        end (str): Event end time
    
    Returns:
        dict: {"status": <status>, "id": <id>}
    """
    url = "http://localhost:5678/webhook/4bf897c5-dfe6-47b2-9d1d-49c7cd28e29d"
    
    payload = {
        "title": title,
        "start": start,
        "end": end
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract status and id from response
        if "response" in data:
            response_data = data["response"]
            return {
                "status": response_data.get("status"),
                "id": response_data.get("id")
            }
        
        return {"status": None, "id": None}
        
    except requests.exceptions.Timeout:
        return {"status": "error", "id": None, "error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "id": None, "error": "Connection failed - is n8n running?"}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "id": None, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"status": "error", "id": None, "error": str(e)}


# Test with debug info
if __name__ == "__main__":
    print("Testing mark_calendar...")
    result = mark_calendar(
        title="Test Meeting",
        start="2026-01-15T10:00:00+05:00",
        end="2026-01-15T11:00:00+05:00"
    )
    print(result)