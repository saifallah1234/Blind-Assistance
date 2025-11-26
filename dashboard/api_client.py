import requests

API_URL = "http://localhost:5000/api"   # your Flask backend

def get_latest():
    try:
        return requests.get(f"{API_URL}/sensor/latest").json()
    except Exception as e:
        return {"error": str(e)}

def get_all(limit=200):
    try:
        return requests.get(f"{API_URL}/sensor/all?limit={limit}").json()
    except Exception as e:
        return []
