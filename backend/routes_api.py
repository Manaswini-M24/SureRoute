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
    """Update stop status (departed/delayed/on-time) from driver or passenger"""

    driver_uid = request.get("driver_uid", "unknown")   # can be passenger string too
    route_id = request.get("route_id")
    stop_id = request.get("stop_id")
    status = request.get("status")                     # e.g., "departed", "delayed", "on-time"
    timestamp = request.get("timestamp")               # frontend sends ISO timestamp
    delay_reason = request.get("delay_reason")         # optional

    if not route_id or not stop_id or not status:
        return JSONResponse(
            content={"error": "Missing required fields"},
            status_code=400
        )

    stop_ref = firebase_init.db.collection("route_data").document(route_id).collection("stops").document(stop_id)

    # Get existing stop data (so we don’t overwrite scheduled arrival/departure or static info)
    existing_stop = stop_ref.get()
    stop_data = existing_stop.to_dict() if existing_stop.exists else {}

    # Update only the live-tracking fields
    stop_ref.set({
        "stop_name": stop_data.get("stop_name", stop_id),   # keep original name if exists
        "scheduled_arrival": stop_data.get("scheduled_arrival"),
        "scheduled_departure": stop_data.get("scheduled_departure"),

        # Live update fields
        "status": status,
        "timestamp": timestamp,
        "updated_by": driver_uid,
        "delay_reason": delay_reason if status.lower() == "delayed" else None
    }, merge=True)

    return {"message": f"✅ Stop {stop_id} on {route_id} marked as {status} by {driver_uid}"}
