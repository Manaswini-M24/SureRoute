from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from backend.routes_api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import backend.firebase_init as firebase_init
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
import requests
import json
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

def calculate_delay_previous_stop(route_id: str, current_stop_id: str, trip_id: str):
    """
    Calculate delay at previous stop for the given trip.
    This is a placeholder - you'll need to implement the actual logic.
    """
    try:
        # TODO: Implement actual logic to:
        # 1. Find the previous stop in the route sequence
        # 2. Get the actual arrival time at that stop for this trip
        # 3. Compare with scheduled time to calculate delay
        
        # For now, return a placeholder value
        # You might need to query your trip tracking/GPS data here
        
        # Placeholder logic - replace with actual implementation
        delay = 0.0  # Default to no delay
        
        # Example logic structure (implement based on your data):
        # previous_stop = get_previous_stop_in_route(route_id, current_stop_id)
        # if previous_stop:
        #     actual_time = get_actual_arrival_time(trip_id, previous_stop['stop_id'])
        #     scheduled_time = previous_stop.get('arrival')
        #     if actual_time and scheduled_time:
        #         delay = calculate_time_difference(actual_time, scheduled_time)
        
        return delay
        
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

async def make_eta_prediction(trip_data: dict) -> dict:
    """
    Make ETA prediction using your existing API
    """
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
            "scheduled_arrival": trip_data['arrival'],  # Your API handles time conversion
            "delay_prev_stop": delay_prev_stop,
            "day": day,
            "time_of_day": time_of_day
        }
        
        # Make request to your ETA prediction API
        # Adjust URL based on where your ETA API is running
        eta_api_url = "http://localhost:8000/predict_delay"  # Update this URL
        
        response = requests.post(eta_api_url, json=prediction_request, timeout=10)
        response.raise_for_status()
        
        prediction_result = response.json()
        
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling ETA API: {e}")
        # Fallback to scheduled time
        return {
            "trip_id": trip_data.get('trip_id', f"trip_{trip_data['route_id']}"),
            "route_id": trip_data['route_id'],
            "stop_name": trip_data['stop_name'],
            "scheduled_arrival": trip_data['arrival'],
            "predicted_eta_time": trip_data['arrival'],  # Fallback to scheduled
            "predicted_delay": 0.0,
            "model_version": "fallback"
        }
    except Exception as e:
        print(f"Unexpected error in ETA prediction: {e}")
        return None

# Your main endpoint
@app.get("/api/upcoming_trips/{stop_name}")
async def get_upcoming_trips(stop_name: str):
    """
    Get upcoming bus trips with ETA predictions for a given stop
    """
    try:
        # Step 1: Find stop across all routes
        stops = firebase_init.get_stop_across_routes_by_name(stop_name)
        
        if not stops:
            return []
        
        # Step 2: Filter upcoming trips (max 5)
        upcoming_trips = get_upcoming_trips_for_stops(stops)
        
        if not upcoming_trips:
            return []
        
        # Step 3: Make ETA predictions for each trip
        predicted_trips = []
        
        for trip in upcoming_trips:
            try:
                prediction = await make_eta_prediction(trip)
                if prediction:
                    predicted_trips.append(prediction)
            except Exception as e:
                print(f"Error predicting for trip {trip}: {e}")
                # Add fallback data
                predicted_trips.append({
                    "trip_id": f"trip_{trip['route_id']}",
                    "route_id": trip['route_id'],
                    "stop_name": trip['stop_name'],
                    "scheduled_arrival": trip['arrival'],
                    "predicted_eta_time": trip['arrival'],
                    "predicted_delay": 0.0,
                    "model_version": "error_fallback"
                })
        
        return predicted_trips
        
    except Exception as e:
        print(f"Error in get_upcoming_trips for '{stop_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trips for stop: {stop_name}")

# Example response format that your frontend expects:
"""
[
  {
    "trip_id": "trip_001",
    "route_id": "route_a",
    "stop_name": "Main Street",
    "scheduled_arrival": "14:30",
    "predicted_eta_time": "14:35",
    "predicted_delay": 5.2,
    "model_version": "xgboost-v1"
  },
  {
    "trip_id": "trip_002", 
    "route_id": "route_b",
    "stop_name": "Main Street",
    "scheduled_arrival": "15:00",
    "predicted_eta_time": "15:00",
    "predicted_delay": 0.0,
    "model_version": "rule-based-v1"
  }
]
"""
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
