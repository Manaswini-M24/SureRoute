from fastapi import APIRouter
from fastapi.responses import JSONResponse
import backend.firebase_init as firebase_init

router = APIRouter()


@router.get("/routes")
def list_routes():
    """Return all routes for dropdown"""
    routes = firebase_init.get_routes()
    # Only send what's needed for frontend
    data = [{"route_id": r["route_id"], "route_no": r["route_no"], "destination": r["destination"]} for r in routes]
    return JSONResponse(content=data)


@router.get("/stops/{route_id}")
def list_stops(route_id: str):
    """Return all stops for a given route"""
    stops = firebase_init.get_stops_for_route(route_id)
    data = [{"stop_id": s["stop_id"], "stop_name": s["stop_name"]} for s in stops]
    return JSONResponse(content=data)


@router.get("/stops_by_name/{stop_name}")
def stops_by_name(stop_name: str):
    """Return all stops across routes by name"""
    stops = firebase_init.get_stop_across_routes_by_name(stop_name)
    data = [{"stop_id": s["stop_id"], "stop_name": s["stop_name"], "route_id": s["route_id"]} for s in stops]
    return JSONResponse(content=data)

@router.post("/driver/update-stop-status")
def update_stop_status(request: dict):
    """Update stop status (arrived/delayed)"""
    driver_uid = request.get("driver_uid")
    route_id = request.get("route_id")
    stop_id = request.get("stop_id")
    status = request.get("status")
    timestamp = request.get("timestamp")
    
    # Update your database with the stop status
    # This depends on your Firebase structure
    # firebase_init.update_stop_status(driver_uid, route_id, stop_id, status, timestamp)
    
    return {"message": f"Stop {stop_id} marked as {status}"}