from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from backend.routes_api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime,timezone,timedelta
import backend.firebase_init as firebase_init
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
import importlib.util
import sys
import os
import re
app = FastAPI()
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
module_path = os.path.join("ai_services", "sureroute-eta-predictor", "app.py")
spec = importlib.util.spec_from_file_location("sureroute_app", module_path)
sureroute_app = importlib.util.module_from_spec(spec)
sys.modules["sureroute_app"] = sureroute_app
spec.loader.exec_module(sureroute_app)

ml_model = sureroute_app.ml_model
db = firebase_init.db
class PredictRequest(BaseModel):
    trip_id: str
    stop_id: str
    scheduled_arrival: str
    delay_prev_stop: float
    day: str
    time_of_day: str

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
        # Find previous stop
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

        #PParse scheduled time (combine with today’s date)
        today = date.today()
        scheduled_dt = datetime.strptime(scheduled_time_str, "%H:%M")
        scheduled_dt = datetime.combine(today, scheduled_dt.time())

        # Parse actual time if exists
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


def normalize_stop_id(stop_id: str) -> str:
    """
    Normalize stop_id to a consistent format.
    Accepts things like r1a_s18, r01_s18, etc.
    """
    if not stop_id:
        return stop_id
    
    parts = stop_id.split("_")
    if len(parts) == 2 and parts[0].startswith("r") and parts[1].startswith("s"):
        route = parts[0][1:]   # after "r"
        stop = parts[1][1:]    # after "s"
        return f"r{route}_s{stop}"
    
    return stop_id  # leave unchanged if unexpected format

def get_upcoming_trips_for_stops(stops: list) -> list:
    """
    Filter upcoming trips (max 5) where scheduled arrival > current time.
    Handles late-night/early-morning rollover.
    """
    current_time = datetime.now().time()
    current_minutes = current_time.hour * 60 + current_time.minute
    
    upcoming_trips = []
    
    for stop in stops:
        # Normalize stop_id so formats like r1a_s18 won't break
        stop["stop_id"] = normalize_stop_id(stop.get("stop_id", ""))
        
        arrival_time = stop.get("arrival")
        if not arrival_time:
            continue
            
        # Convert arrival time to minutes for comparison
        arrival_minutes = time_string_to_minutes(arrival_time)
        
        # Check if trip is upcoming (handle day rollover)
        if arrival_minutes > current_minutes or (
            arrival_minutes < 360 and current_minutes > 1320
        ):
            upcoming_trips.append(stop)
    
    # Sort by arrival time and limit to 5
    upcoming_trips.sort(key=lambda x: time_string_to_minutes(x.get("arrival", "00:00")))
    return upcoming_trips[:5]

DAY_MAPPING = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}
TIME_MAPPING = {
    "morning": 0,    # 05:00–12:00
    "afternoon": 1,  # 12:00–17:00
    "evening": 2,    # 17:00–21:00
    "night": 3       # 21:00–05:00
}

def run_model_prediction(prediction_request: dict) -> dict:
    if ml_model is None:
        raise RuntimeError("ML model not loaded")

    # Detect which model is being used
    model_type = type(ml_model).__name__
    n_features = getattr(ml_model, "n_features_in_", None)

    print(f"✅ Using model: {model_type}, expects {n_features} features")

    # Encode categorical features
    day_encoded = DAY_MAPPING.get(prediction_request["day"], 1)
    time_encoded = TIME_MAPPING.get(prediction_request["time_of_day"], 2)
    scheduled_minutes = time_string_to_minutes(prediction_request["scheduled_arrival"])

    # Choose features based on model
    if n_features == 2:
        features = [scheduled_minutes, float(prediction_request["delay_prev_stop"])]
    elif n_features == 4:
        features = [
            scheduled_minutes,
            float(prediction_request["delay_prev_stop"]),
            day_encoded,
            time_encoded,
        ]
    else:
        raise RuntimeError(f"Unsupported model feature size: {n_features}")

    predicted_delay = ml_model.predict([features])[0]

    # Add delay to scheduled arrival
    predicted_eta_minutes = scheduled_minutes + predicted_delay
    hours, minutes = divmod(int(predicted_eta_minutes), 60)
    predicted_eta_time = f"{hours:02d}:{minutes:02d}"

    return {
        "trip_id": prediction_request["trip_id"],
        "predicted_eta_time": predicted_eta_time,
        "predicted_delay": float(predicted_delay),
        "model_version": "v1.0",
        "model_used": model_type,        
        "features_expected": n_features  
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
        
        #  Direct model call instead of HTTP
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

@app.get("/api/upcoming_trips/{stop_name}")
async def get_upcoming_trips(stop_name: str):
    """
    Get upcoming bus trips with ETA predictions for a given stop.
    stop_name like 'r44a_s13' → route_44-A/stops/stop_13
    """
    try:
        # 🔹 Parse stop name
        match = re.match(r"r([a-z0-9\-]+)_s([a-z0-9]+)", stop_name.lower())
        if not match:
            raise HTTPException(status_code=400, detail="Invalid stop format. Use rXX_sYY")

        raw_route = match.group(1)   # e.g. "44a" or "44-a"
        stop_num = match.group(2)    # e.g. "13"

        # 🔹 Convert to Firestore format
        #   - Insert hyphen before trailing letters
        #   - Keep uppercase letters (for Firestore consistency)
        route_id = re.sub(r"(\d+)([a-z])$", r"\1-\2", raw_route, flags=re.IGNORECASE)
        route_id = f"route_{route_id.upper()}"  # Firestore uses uppercase suffix
        stop_id = f"stop_{stop_num}"

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
    port = int(os.getenv("PORT", 8000))  # use Render's port if available
    uvicorn.run("main:app", host="0.0.0.0", port=port)
