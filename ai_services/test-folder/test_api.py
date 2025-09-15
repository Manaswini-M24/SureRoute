import requests
import json

test_data = {
    "trip_id": "BUS_51D_001",
    "stop_id": "r51d_s5",
    "scheduled_arrival": 450.0,
    "delay_prev_stop": 5.0,
    "day": "monday",
    "time_of_day": "morning_rush"
}

try:
    # CHANGE PORT 7860 TO 8000 ↓
    response = requests.post(
        "http://localhost:8000/predict_delay",  # ← Changed to 8000!
        json=test_data,
        timeout=5
    )
    
    print("✅ API Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except requests.exceptions.ConnectionError:
    print("❌ API is not running! Start it with: uvicorn app:app --reload")
except Exception as e:
    print(f"❌ Error: {e}")