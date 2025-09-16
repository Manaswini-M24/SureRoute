import os
import firebase_admin
from firebase_admin import credentials, firestore
import re
# -----------------------------
# Firebase Initialization
# -----------------------------
cred_path = os.environ.get("FIREBASE_PATH", "serviceAccountKey.json")

if not firebase_admin._apps:  # Prevent re-init error
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()


# -----------------------------
# Helper: Get all routes
# -----------------------------
def get_routes():
    """
    Fetches all routes from 'mangaluru_buses'.
    Each document has fields: route_no, destination, source, etc.
    """
    routes_ref = db.collection("mangaluru_buses")
    docs = routes_ref.stream()
    routes = []

    for doc in docs:
        data = doc.to_dict() or {}
        routes.append({
            "route_id": doc.id,
            "route_no": data.get("route_no"),
            "destination": data.get("destination"),
            "source": data.get("source"),
        })

    return routes


# -----------------------------
# Helper: Get stops for a route
# -----------------------------
def get_stops_for_route(route_id: str):
    """
    Fetches stops under a specific route.
    """
    stops_ref = db.collection("mangaluru_buses").document(route_id).collection("stops")
    docs = stops_ref.stream()
    stops = []

    for doc in docs:
        data = doc.to_dict() or {}
        stops.append({
            "stop_id": data.get("id") or doc.id,
            "stop_name": data.get("name"),
            "arrival": data.get("arrival"),
            "departure": data.get("departure"),
        })

    return stops


# -----------------------------
# Helper: Get stop across routes
# -----------------------------
def get_stop_across_routes_by_name(stop_name: str):
    """
    Finds all occurrences of a stop across routes using the stop name.
    """
    try:
        query = db.collection_group("stops").where("name", "==", stop_name)
        docs = query.stream()
        stops = []

        for doc in docs:
            data = doc.to_dict() or {}
            stops.append({
                "route_id": doc.reference.parent.parent.id,  # parent route
                "stop_id": data.get("id") or doc.id,        # still store ID for backend
                "stop_name": data.get("name"),
                "arrival": data.get("arrival"),
                "departure": data.get("departure"),
            })

        if not stops:
            print(f"⚠️ No matches found for stop_name='{stop_name}'")
        return stops

    except Exception as e:
        print(f"❌ Error in get_stop_across_routes_by_name for '{stop_name}': {e}")
        return []

# def normalize_stop_id(stop_id: str, existing_doc_ids: list[str]) -> str | None:
#     # extract trailing number (from r22_s15 → 15)
#     m = re.search(r"(\d+)$", stop_id)
#     if not m:
#         return None
#     num = m.group(1)
#     candidate = f"stop_{num}"

#     if candidate in existing_doc_ids:
#         return candidate
#     return None

# def update_stop_status(driver_uid: str, route_id: str, stop_id: str, status: str, timestamp: str, reason: str = None):
#     stops_coll = db.collection("route_data").document(route_id).collection("stops")

#     # list all docs first
#     existing_ids = [doc.id for doc in stops_coll.stream()]

#     # normalize given stop_id to match existing doc ids
#     normalized_id = normalize_stop_id(stop_id, existing_ids)
#     if not normalized_id:
#         raise ValueError(f"No matching stop doc found for '{stop_id}' in route '{route_id}'. Existing: {existing_ids}")

#     stop_ref = stops_coll.document(normalized_id)

#     update_data = {
#         "status": status,
#         "last_updated_by": driver_uid,
#         "last_updated": timestamp
#     }
#     if reason:
#         update_data["reason"] = reason

#     stop_ref.update(update_data)
#     return {"ok": True, "updated_doc": normalized_id}
