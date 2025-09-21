# SureRoute

**Real-time bus ETA prediction system for cities like Mangaluru.**  
SureRoute helps bus commuters reduce uncertainty by providing real-time information on bus routes, stops, and AI-predicted arrival times.

---
#Deployment link
**https://sureroute.onrender.com**
---
#Demo video
**https://drive.google.com/drive/folders/1itvHw-ByOe89FnepSaRePnl11gZXPK5Q?usp=drive_link**
---
## Features

- **Passenger Portal** – Find upcoming buses and report issues easily.  
- **Driver Portal** – Drivers update stop status in real time.  
- **Live ETA Predictions** – AI-powered predictions using delays at previous stops.  
- **Accurate Delay Tracking** – Adjusted ETAs instead of just scheduled times.  
- **Firestore Integration** – All route and stop data stored in the cloud.

---

## Tech Stack

### Frontend
- **HTML / CSS / JavaScript** – for the Passenger and Driver portals  
- **Jinja2 Templates** – for dynamic rendering in FastAPI  
- **Leaflet.js (optional)** – for map/route visualization  

### Backend
- **Python** – main programming language  
- **FastAPI** – web framework for APIs and server-side routing  
- **APScheduler** – for scheduled tasks like resetting route data  
- **Pydantic** – for data validation in API requests  

### Database
- **Firebase Firestore** – storing routes, stops, and real-time status updates  

### AI / ML
- **Scikit-learn / XGBoost** – for ETA prediction model  
- **Joblib** – saving/loading trained ML model  

### Deployment / Dev Tools
- **Uvicorn** – ASGI server for FastAPI  
- **CORS Middleware** – enabling cross-origin requests  

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Manaswini-M24/SureRoute.git
cd SureRoute

# 2. Set up and activate a virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
uvicorn main:app --reload
