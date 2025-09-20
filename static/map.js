// ---- Initialize Leaflet Map ----
const map = L.map('map').setView([12.9716, 77.5946], 13);

// OpenStreetMap Tile Layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
}).addTo(map);

// ---- Custom Icons ----
const userIcon = L.icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/149/149071.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

const stopIcon = L.icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png", // normal stop
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -28]
});

const nearbyStopIcon = L.icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/190/190411.png", // highlighted stop
  iconSize: [30, 30],
  iconAnchor: [15, 30],
  popupAnchor: [0, -30]
});

// ---- Store Stops Globally ----
let allStops = [];

// ---- Fetch Bus Stops from Firestore ----
async function loadStops() {
  const res = await fetch("/stops");
  const data = await res.json();
  console.log("Stops loaded:", data.stops);

  data.stops.forEach((stop) => {
    if (stop.latitude && stop.longitude) {
      L.marker([stop.latitude, stop.longitude], { icon: stopIcon })
        .addTo(map)
        .bindPopup(`<b>${stop.name}</b><br>Route ${stop.route_no}`);
    }
  });
}
loadStops();


// ---- Distance Calculator (Haversine) ----
function getDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // Earth radius in meters
  const toRad = (deg) => deg * Math.PI / 180;
  const φ1 = toRad(lat1), φ2 = toRad(lat2);
  const Δφ = toRad(lat2 - lat1);
  const Δλ = toRad(lon2 - lon1);

  const a = Math.sin(Δφ / 2) ** 2 +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // distance in meters
}

// ---- Show User Location & Highlight Nearby Stops ----
function trackUserLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }
  console.log("trackUserLocation called");
  console.log("Geolocation supported");
  navigator.geolocation.watchPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      console.log("Got position:", position);
      // Update or create user marker
      if (window.userMarker) {
        window.userMarker.setLatLng([lat, lng]);
      } else {
        window.userMarker = L.marker([lat, lng], { icon: userIcon })
          .addTo(map)
          .bindPopup("<b>You are here</b>")
          .openPopup();
      }

      // Center map first time
      if (!window.userCentered) {
        map.setView([lat, lng], 14);
        window.userCentered = true;
      }

      // Highlight nearby stops within 1 km
      allStops.forEach((stop) => {
        const dist = getDistance(lat, lng, stop.latitude, stop.longitude);
        if (dist <= 1000) { // within 1 km
          stop.marker.setIcon(nearbyStopIcon);
          stop.marker.bindPopup(
            `<b>${stop.name}</b><br>Route ${stop.route_no || ''}<br>🚏 Nearby Stop (${Math.round(dist)} m)`
          );
          console.log("allStops length:", allStops ? allStops.length : "undefined");
        } else {
          stop.marker.setIcon(stopIcon); // reset to normal
        }
      });
    },
    (err) => {
      console.error("Location error:", err);
      alert("Unable to get your location.");
    },
    { enableHighAccuracy: true }
  );
}

// ---- Run Everything ----
// loadStops();
// trackUserLocation();
// Button click → show map + init + call your existing function
document.getElementById("use-location").addEventListener("click", () => {
    const el = document.getElementById("map");
    
    // Show map container properly
    el.style.display = "block";
    el.style.height = "400px";
    el.style.width = "100%";
    
    // Only initialize once
    if (!window.map) {
        window.map = L.map("map");
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; OpenStreetMap contributors',
        }).addTo(window.map);
    }
    
    // 🔑 Multiple invalidateSize calls with longer delay
   // after the div is visible
setTimeout(() => map.invalidateSize(), 50);

    
    // Start tracking location
    trackUserLocation();
});