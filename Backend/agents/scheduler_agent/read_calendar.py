import requests

def read_calendar_events():
    url = "http://localhost:5678/webhook/a02479d5-bb46-40ab-9b03-7ebbd47f8a0d"
    response = requests.get(url)
    data = response.json()
    return data['calendar_events']