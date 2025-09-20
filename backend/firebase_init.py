import os
import firebase_admin
from firebase_admin import credentials, firestore
import re

cred_path = os.environ.get("FIREBASE_PATH", "serviceAccountKey.json")

if not firebase_admin._apps:  # Prevent re-init error
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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
