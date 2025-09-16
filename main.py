from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from backend.routes_api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime,timezone,timedelta
import backend.firebase_init as firebase_init
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
import requests
import json
import joblib
import os

MODEL_PATH = os.path.join("ai_services", "sureroute-eta-predictor", "models", "xgboost_eta_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Make sure the submodule is initialized and updated.")
ml_model = joblib.load(MODEL_PATH)
print("✅ ML model loaded successfully:", type(ml_model))
app = FastAPI()
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)

db = firebase_init.db
class PredictRequest(BaseModel):
    trip_id: str
    stop_id: str
    scheduled_arrival: str
    delay_prev_stop: float
    day: str
    time_of_day: str
def load_model():
    global model
    model=joblib.load("ai_services/model_trianing/xgboost_eta_model.pkl")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/driver", response_class=HTMLResponse)
async def driver(request: Request):
    return templates.TemplateResponse("driver.html", {"request": request})
@app.get("/passenger", response_class=HTMLResponse)
async def passenger(request: Request):
    return templates.TemplateResponse("passenger.html", {"request": request})
def reset_route_data():
    routes = db.collection("route_data").stream()
    for route_doc in routes:
        route_id = route_doc.id
        stops = db.collection("route_data").document(route_id).collection("stops").stream()
        for stop_doc in stops:
            stop_doc.reference.update({
                "status": None,
                "last_updated": None,
                "updated_by": None
            })
    print("🔄 Reset all route_data stops")

# Schedule at midnight UTC
scheduler = BackgroundScheduler()
scheduler.add_job(reset_route_data, "cron", hour=0, minute=0)
scheduler.start()
def get_current_time_info():
    """Get current day and time_of_day classification"""
    now = datetime.now()
    
    # Get day of week
    day = now.strftime("%A")  # Monday, Tuesday, etc.
    
    # Get time of day classification
    hour = now.hour
    if 5 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 17:
        time_of_day = "afternoon"
    elif 17 <= hour < 21:
        time_of_day = "evening"
    else:
        time_of_day = "night"
    
    return day, time_of_day

def time_string_to_minutes(time_str: str) -> float:
    """Convert time string (HH:MM or HH:MM:SS) to minutes past midnight"""
    try:
        # Handle both HH:MM and HH:MM:SS formats
        if len(time_str.split(':')) == 3:
            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
        else:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        
        return time_obj.hour * 60 + time_obj.minute
    except ValueError as e:
        print(f"Error parsing time string '{time_str}': {e}")
        return 0.0



from datetime import datetime, date

def calculate_delay_previous_stop(route_id: str, current_stop_id: str, trip_id: str):
    """
    Calculate delay at previous stop for the given trip.
    Uses scheduled arrival and last_updated fields from Firestore.
    """
    try:
        # 1️⃣ Find previous stop
        stops_ref = db.collection("route_data").document(route_id).collection("stops")
        stops_docs = list(stops_ref.stream())
        stops_docs.sort(key=lambda d: d.id)  # Assuming doc ids are stop_1, stop_2, etc.

        prev_stop_doc = None
        for i, doc in enumerate(stops_docs):
            if doc.id == current_stop_id and i > 0:
                prev_stop_doc = stops_docs[i-1]
                break

        if not prev_stop_doc:
            return 0.0  # No previous stop

        prev_data = prev_stop_doc.to_dict() or {}

        scheduled_time_str = prev_data.get("scheduled_arrival")  # e.g., '07:00'
        actual_time_str = prev_data.get("last_updated")          # e.g., '2025-09-15T07:05:00'

        if not scheduled_time_str:
            return 0.0

        # 2️⃣ Parse scheduled time (combine with today’s date)
        today = date.today()
        scheduled_dt = datetime.strptime(scheduled_time_str, "%H:%M")
        scheduled_dt = datetime.combine(today, scheduled_dt.time())

        # 3️⃣ Parse actual time if exists
        if actual_time_str:
            # Remove Z if present
            actual_time_str = actual_time_str.replace("Z", "")
            actual_dt = datetime.fromisoformat(actual_time_str)
            delay_minutes = (actual_dt - scheduled_dt).total_seconds() / 60.0
        else:
            delay_minutes = 0.0

        return delay_minutes

    except Exception as e:
        print(f"Error calculating delay for trip {trip_id}: {e}")
        return 0.0


def get_upcoming_trips_for_stops(stops: list) -> list:
    """
    Filter upcoming trips (max 5) where scheduled arrival > current time
    """
    current_time = datetime.now().time()
    current_minutes = current_time.hour * 60 + current_time.minute
    
    upcoming_trips = []
    
    for stop in stops:
        arrival_time = stop.get('arrival')
        if not arrival_time:
            continue
            
        # Convert arrival time to minutes for comparison
        arrival_minutes = time_string_to_minutes(arrival_time)
        
        # Check if trip is upcoming (handle day rollover)
        if arrival_minutes > current_minutes or (arrival_minutes < 360 and current_minutes > 1320):  # Handle late night/early morning
            upcoming_trips.append(stop)
    
    # Sort by arrival time and limit to 5
    upcoming_trips.sort(key=lambda x: time_string_to_minutes(x.get('arrival', '00:00')))
    return upcoming_trips[:5]
def run_model_prediction(prediction_request: dict) -> dict:
    """
    Run the ML model directly instead of making an API call.
    """
    # Extract features from the request
    features = [
        prediction_request["delay_prev_stop"],
        prediction_request["day"],
        prediction_request["time_of_day"],
        # add more features if your model expects them
    ]
    
    # Get prediction
    predicted_delay = model.predict([features])[0]
    
    # Compute ETA = scheduled + delay
    predicted_eta_time = prediction_request["scheduled_arrival"] + predicted_delay
    
    return {
        "trip_id": prediction_request["trip_id"],
        "predicted_eta_time": predicted_eta_time,
        "predicted_delay": float(predicted_delay),
        "model_version": "v1.0"
    }
async def make_eta_prediction(trip_data: dict) -> dict:
    try:
        # Get current day and time_of_day
        day, time_of_day = get_current_time_info()
        
        # Calculate delay at previous stop
        delay_prev_stop = calculate_delay_previous_stop(
            trip_data['route_id'], 
            trip_data['stop_id'], 
            trip_data.get('trip_id', f"trip_{trip_data['route_id']}")
        )
        
        # Prepare prediction request
        prediction_request = {
            "trip_id": trip_data.get('trip_id', f"trip_{trip_data['route_id']}"),
            "stop_id": trip_data['stop_id'],
            "scheduled_arrival": trip_data['arrival'],
            "delay_prev_stop": delay_prev_stop,
            "day": day,
            "time_of_day": time_of_day
        }
        
        # ✅ Direct model call instead of HTTP
        prediction_result = run_model_prediction(prediction_request)
        
        # Combine original trip data with prediction
        return {
            "trip_id": prediction_result['trip_id'],
            "route_id": trip_data['route_id'],
            "stop_name": trip_data['stop_name'],
            "scheduled_arrival": trip_data['arrival'],
            "predicted_eta_time": prediction_result['predicted_eta_time'],
            "predicted_delay": round(prediction_result['predicted_delay'], 1),
            "model_version": prediction_result['model_version']
        }
        
    except Exception as e:
        print(f"Unexpected error in ETA prediction: {e}")

        # Calculate previous stop delay
        prev_delay = calculate_delay_previous_stop(
            route_id=trip_data['route_id'],
            current_stop_id=trip_data['stop_id'],
            trip_id=trip_data.get('trip_id', f"trip_{trip_data['route_id']}")
        )

        # Add delay to scheduled arrival
        scheduled_time_str = trip_data['arrival']  # e.g., '07:12'
        today = datetime.today().date()
        scheduled_dt = datetime.strptime(scheduled_time_str, "%H:%M")
        scheduled_dt = datetime.combine(today, scheduled_dt.time())
        predicted_eta_dt = scheduled_dt + timedelta(minutes=prev_delay)
        predicted_eta_str = predicted_eta_dt.strftime("%H:%M")

        return {
            "trip_id": trip_data.get('trip_id', f"trip_{trip_data['route_id']}"),
            "route_id": trip_data['route_id'],
            "stop_name": trip_data['stop_name'],
            "scheduled_arrival": trip_data['arrival'],
            "predicted_eta_time": predicted_eta_str,  # scheduled + previous delay
            "predicted_delay": prev_delay,
            "model_version": "fallback"
        }   


# Your main endpoint
import re

@app.get("/api/upcoming_trips/{stop_name}")
async def get_upcoming_trips(stop_name: str):
    """
    Get upcoming bus trips with ETA predictions for a given stop.
    stop_name will be like 'r42_s3' → route_42/stops/stop_3
    """
    try:
        # 🔹 Parse "r42_s3" → route_id="route_42", stop_id="stop_3"
        match = re.match(r"r(\d+)_s(\d+)", stop_name.lower())
        if not match:
            raise HTTPException(status_code=400, detail="Invalid stop format. Use rXX_sYY")

        route_id = f"route_{match.group(1)}"
        stop_id = f"stop_{match.group(2)}"
        print(f"🔎 Parsed stop_name='{stop_name}' → route_id='{route_id}', stop_id='{stop_id}'")

        # 🔹 Fetch stop doc directly
        stop_ref = firebase_init.db.collection("route_data").document(route_id).collection("stops").document(stop_id)
        doc = stop_ref.get()

        if not doc.exists:
            print(f"⚠️ No document found for {route_id}/{stop_id}")
            return []

        stop_data = doc.to_dict() or {}
        print(f"✅ Found stop data: {stop_data}")

        # 🔹 Build upcoming trips list
        upcoming_trips = [{
            "route_id": route_id,
            "stop_id": stop_id,
            "stop_name": stop_data.get("stop_name", stop_id),
            "arrival": stop_data.get("scheduled_arrival"),
            "departure": stop_data.get("scheduled_departure"),
        }]

        predicted_trips = []
        for trip in upcoming_trips:
            try:
                prediction = await make_eta_prediction(trip)
                if prediction:
                    predicted_trips.append(prediction)
            except Exception as e:
                print(f"⚠️ ETA prediction failed for {trip}: {e}")
                predicted_trips.append({
                    "trip_id": f"trip_{trip['route_id']}",
                    "route_id": trip["route_id"],
                    "stop_name": trip["stop_name"],
                    "scheduled_arrival": trip["arrival"],
                    "predicted_eta_time": trip["arrival"],
                    "predicted_delay": 0.0,
                    "model_version": "fallback"
                })

        return predicted_trips

    except Exception as e:
        print(f"❌ Error in get_upcoming_trips for '{stop_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trips for stop: {stop_name}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
