# test_api.py
import requests
import time

def test_api():
    print("Testing API endpoints...")
    
    endpoints = [
        "http://localhost:8000/",
        "http://localhost:8000/health", 
        "http://localhost:8000/system_status",
        "http://localhost:8000/data_stats"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            start_time = time.time()
            response = requests.get(endpoint, timeout=5)
            end_time = time.time()
            
            print(f"✅ Status: {response.status_code}")
            print(f"⏱️  Response time: {end_time - start_time:.2f}s")
            print(f"📦 Response: {response.json()}")
            
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT: {endpoint} took too long")
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR: API may not be running")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()