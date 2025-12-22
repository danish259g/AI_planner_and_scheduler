import requests
import json

url = "http://127.0.0.1:8000/api/interpret"
payload = {"raw_text": "Team sync from 10am to 11am"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
