# SureRoute AI Services

This module contains the machine learning models for anomaly detection and NLP, exposed as RESTful APIs.

## Setup

1.  Navigate to this directory: `cd ai_services`
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment:
    *   Windows: `.\venv\Scripts\activate`
    *   Mac/Linux: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt` (Note: you might need to create a `requirements.txt` file first with `pip freeze > requirements.txt`)

## Running the Anomaly Detection API

1.  Ensure your virtual environment is activated.
2.  Run: `python app.py`
3.  The server will start on `http://127.0.0.1:5000`

## API Documentation

### Endpoint: `/predict_delay`
## Testing the API

### Using PowerShell (Recommended on Windows)
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/predict_delay" -Method "Post" -ContentType "application/json" -Body '{"scheduled_time": 100, "actual_time": 50}'

# SureRoute ETA Predictor

FastAPI service for predicting bus arrival times.

## API Endpoints
- `POST /predict_delay` - Predict bus delay and ETA
- `GET /docs` - Interactive API documentation

## Local Development
```bash
uvicorn main:app --reload

**API URL:** https://megha-277-sureroute-eta-predictor.hf.space/predict_delay  
> **Docs:** https://megha-277-sureroute-eta-predictor.hf.space/docs  
>   
> The endpoint takes bus trip data and returns predicted delays/ETAs. 

You will see the automatic Swagger UI documentation.

Click on the POST /predict_delay endpoint.

Click "Try it out".

Paste this sample JSON into the request body box:

json
{
  "trip_id": "bus_5A_downtown",
  "stop_id": "stop_central_square",
  "scheduled_arrival": 870.0,
  "delay_prev_stop": 7.5,
  "day": "wednesday",
  "time_of_day": "morning_rush"
}
Click "Execute".

You should get a successful 200 response with the predicted ETA in the response body.

