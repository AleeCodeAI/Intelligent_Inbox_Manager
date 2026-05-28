import requests
from configs import MainSettings

def mark_calendar(title, start, end):
    url = MainSettings().MARK_CALENDAR  
    
    payload = {"title": title, "start": start, "end": end}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "response" in data:
            response_data = data["response"]
            return {
                "status": response_data.get("status"),
                "id": response_data.get("id")
            }
        
        # Surface unexpected structure instead of silently returning None
        return {"status": "error", "id": None, "error": f"Unexpected response structure: {data}"}
        
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
        start="2026-05-28T09:00:00+05:00",
        end="2026-05-28T18:30:00+05:00"
    )
    print(result)