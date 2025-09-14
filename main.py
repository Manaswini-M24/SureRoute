from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from backend.routes_api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import backend.firebase_init as firebase_init
from apscheduler.schedulers.background import BackgroundScheduler
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
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
