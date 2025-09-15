from fastapi import APIRouter
from fastapi.responses import JSONResponse
import backend.firebase_init as firebase_init
import re
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

def normalize_stop_id(stop_id: str, stops_coll):
    """Try to map r22_s15, s15, 15 → stop_15 if it exists in Firestore."""
    # 1) If already stop_<n>, keep it
    if re.match(r"^stop_\d+$", stop_id):
        if stops_coll.document(stop_id).get().exists:
            return stop_id

    # 2) Extract trailing digits (s15 → 15, r22_s15 → 15)
    m = re.search(r"(\d+)$", stop_id)
    if m:
        candidate = f"stop_{m.group(1)}"
        if stops_coll.document(candidate).get().exists:
            return candidate

    # 3) Fall back: only return original if it actually exists
    if stops_coll.document(stop_id).get().exists:
        return stop_id

    return None


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

    stops_coll = firebase_init.db.collection("route_data").document(route_id).collection("stops")

    # normalize stop_id so it points to an *existing* document
    normalized_id = normalize_stop_id(stop_id, stops_coll)
    if not normalized_id:
        return JSONResponse(
            content={"error": f"No stop document found for stop_id '{stop_id}' in route '{route_id}'"},
            status_code=404
        )

    stop_ref = stops_coll.document(normalized_id)

    # Get existing stop data (so we don’t overwrite scheduled info)
    existing_stop = stop_ref.get()
    stop_data = existing_stop.to_dict() if existing_stop.exists else {}

    # Update only the live-tracking fields
    stop_ref.update({
        "stop_name": stop_data.get("stop_name", normalized_id),
        "scheduled_arrival": stop_data.get("scheduled_arrival"),
        "scheduled_departure": stop_data.get("scheduled_departure"),

        # Live fields
        "status": status,
        "last_updated": timestamp,        # ✅ overwrite the correct field
        "last_updated_by": driver_uid,
        "reason": delay_reason if status.lower() == "delayed" else None
    })

    return {"message": f"✅ Stop {normalized_id} on {route_id} marked as {status} by {driver_uid}"}