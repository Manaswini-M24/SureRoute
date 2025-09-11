import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os



# ---- CONFIG ----
FIREBASE_KEY_FILE = "serviceAccountKey.json"   # Firebase private key
ROUTES_JSON_FILE = "routes.json"               # Your routes JSON
ORS_API_KEY = os.getenv("ORS_API_KEY") 



if not ORS_API_KEY:
    raise ValueError("❌ ORS_API_KEY not set! Please set it in your environment.")
 # OpenRouteService API Key
# ---- INIT FIREBASE ----
cred = credentials.Certificate(FIREBASE_KEY_FILE)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---- GEOCODING FUNCTION ----
def fetch_coordinates(place_name):
    url = f"https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": ORS_API_KEY,
        "text": f"{place_name}, Mangaluru, Karnataka, India",
        "boundary.country": "IN"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        coords = data["features"][0]["geometry"]["coordinates"]
        return coords[1], coords[0]  # (lat, lng)
    except Exception as e:
        print(f"⚠️ Could not fetch coords for {place_name}: {e}")
        return None, None

# ---- LOAD ROUTES JSON ----
with open(ROUTES_JSON_FILE, "r") as f:
    routes_data = json.load(f)

# ---- PROCESS & UPLOAD ----
for route in routes_data:
    route_doc = {
        "route_no": route["route_no"],
        "source": route["source"],
        "destination": route["destination"],
        "frequency_minutes": route.get("frequency_minutes", 60),
        "via": route.get("via", [])
    }
    
    # Create document under collection
    route_ref = db.collection("mangaluru_buses").document(f"route_{route['route_no']}")
    route_ref.set(route_doc)

    for i, stop in enumerate(route["stops"], start=1):
        # Auto-fill missing lat/lng
        if "latitude" not in stop or "longitude" not in stop:
            lat, lng = fetch_coordinates(stop["name"])
            if lat and lng:
                stop["latitude"], stop["longitude"] = lat, lng

        stop_ref = route_ref.collection("stops").document(f"stop_{i}")
        stop_ref.set(stop)
    
    print(f"✅ Uploaded route {route['route_no']} with {len(route['stops'])} stops")

print("🎉 All routes uploaded successfully to Firestore!")
