from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import numpy as np

app = FastAPI(
    title="SureRoute ETA Prediction API",
    description="API for predicting bus arrival times", 
    version="1.0.0"
)

class PredictionRequest(BaseModel):
    trip_id: str
    stop_id: str
    scheduled_arrival: float
    delay_prev_stop: float
    day: str
    time_of_day: str

class PredictionResponse(BaseModel):
    trip_id: str
    stop_id: str
    predicted_delay: float
    predicted_eta: float
    model_version: str = "rule-based-v1"

@app.post("/predict_delay", response_model=PredictionResponse)
async def predict_delay(request: PredictionRequest):
    predicted_delay = request.delay_prev_stop
    predicted_eta = request.scheduled_arrival + predicted_delay
    
    return PredictionResponse(
        trip_id=request.trip_id,
        stop_id=request.stop_id, 
        predicted_delay=predicted_delay,
        predicted_eta=predicted_eta
    )

@app.get("/")
async def root():
    return {"message": "SureRoute ETA Prediction Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}