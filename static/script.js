// SureRoute Application Logic

// Global state
let currentPage = 'landing';
let currentStops = [];
let currentStopIndex = 0;
// let driverStatus = 'on-time';
// let passengerStatus = 'on-time';
// let driverEta = '2 minutes to next stop';
// let passengerEta = '5 minutes';

// let activityLog = [ 
//   { id: 1, timestamp: new Date(), action: 'Route started', type: 'driver' }
// ];
const departedBtn = document.getElementById("departed-btn");
const delayReasonSelect = document.getElementById("delay-reason-select");
const delayFlagBtn = document.getElementById("delay-flag-btn");
const delayMessage = document.getElementById("delay-message");
let notifications = [
  { id: 1, timestamp: new Date(), message: 'Bus tracking started', type: 'info' }
];

// DOM Elements for pages and nav buttons
const pages = {
  landing: document.getElementById('landing-page'),
  driver: document.getElementById('driver-page'),
  passenger: document.getElementById('passenger-page'),
};
const navBtns = {
  home: document.getElementById('home-btn'),
  driver: document.getElementById('driver-btn'),
  passenger: document.getElementById('passenger-btn'),
  driverAccount: document.getElementById('driver-account-btn'),
};

// Navigation function to show selected page and update nav buttons
function showPage(pageName) {
  Object.values(pages).forEach(page => page.classList.add('hidden'));
  pages[pageName].classList.remove('hidden');

  Object.values(navBtns).forEach(btn => btn.classList.remove('active'));
  if (pageName === 'landing') {
    navBtns.home.classList.add('active');
  } else if (navBtns[pageName]) {
    navBtns[pageName].classList.add('active');
  }
  currentPage = pageName;
}


// Entry point
function initApp() {
  console.log("App initialized");

  // Load routes when page loads
  loadRoutes();
  loadReportRoutes();
  renderDriverStops();
  event.preventDefault();
  loadSignupRoutes();
  // Add other new functions if needed
  // renderLandingPage();
  // setupEventListeners();
  // etc.
}

// Run after DOM is loaded
document.addEventListener("DOMContentLoaded", initApp);

// ---------------------------
// Driver Account Modal Logic
// ---------------------------

function openAccountModal() {
  document.getElementById('account-modal').classList.remove('hidden');
  switchTab('login'); // default to login tab
}

function closeAccountModal() {
  document.getElementById('account-modal').classList.add('hidden');
}

// Tab switching between login and signup forms
function switchTab(tab) {
  const loginTabBtn = document.getElementById('tab-login');
  const signupTabBtn = document.getElementById('tab-signup');
  const loginForm = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');

  if (tab === 'login') {
    loginTabBtn.classList.add('active');
    signupTabBtn.classList.remove('active');
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
  } else {
    loginTabBtn.classList.remove('active');
    signupTabBtn.classList.add('active');
    loginForm.classList.remove('active');
    signupForm.classList.add('active');
  }
}

// ✅ Login
// LOGIN FORM CODE (login.js or in your login page)
document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const email = form.email.value;
  const password = form.password.value;

  try {
    const userCredential = await auth.signInWithEmailAndPassword(email, password);
    const user = userCredential.user;

    // Get Firebase ID token (to send to Flask later if needed)
    const idToken = await user.getIdToken();

    // 🔹 Fetch driver's assigned route from Firestore
    const driverDoc = await db.collection("drivers").doc(user.uid).get();
    if (!driverDoc.exists) {
      throw new Error("Driver profile not found in Firestore.");
    }
    const driverData = driverDoc.data();
    const selectedRouteId = driverData.bus_route; // assuming field name is bus_route

    // Store in localStorage for later use
    localStorage.setItem("selectedRouteId", selectedRouteId);
    localStorage.setItem("driverUid", user.uid); // Store driver UID as well

    console.log("Stored routeId:", selectedRouteId); // Debug log

    // Redirect to driver dashboard
    window.location.href = "/driver";

  } catch (error) {
    console.log("Firebase error:", error); // For debugging
    
    let message = "Login failed!";
    
    // Check if error.message contains JSON (REST API error format)
    if (typeof error.message === 'string' && error.message.includes('"error"')) {
      try {
        const errorObj = JSON.parse(error.message);
        const errorCode = errorObj.error?.message;
        
        if (errorCode === "INVALID_LOGIN_CREDENTIALS") {
          message = "Invalid email or password.";
        } else if (errorCode === "EMAIL_NOT_FOUND") {
          message = "No account found with this email.";
        } else if (errorCode === "INVALID_PASSWORD") {
          message = "Incorrect password.";
        } else if (errorCode === "INVALID_EMAIL") {
          message = "Invalid email format.";
        } else if (errorCode === "TOO_MANY_ATTEMPTS_TRY_LATER") {
          message = "Too many failed attempts. Please try again later.";
        } else if (errorCode === "USER_DISABLED") {
          message = "This account has been disabled.";
        } else {
          message = `Login failed: ${errorCode || 'Unknown error'}`;
        }
      } catch (parseError) {
        message = "Login failed: Invalid credentials.";
      }
    } 
    // Handle standard Firebase SDK error codes
    else if (error.code === "auth/user-not-found") {
      message = "No account found with this email.";
    } else if (error.code === "auth/wrong-password") {
      message = "Incorrect password.";
    } else if (error.code === "auth/invalid-email") {
      message = "Invalid email format.";
    } else if (error.code === "auth/invalid-credential" || error.code === "auth/invalid-login-credentials") {
      message = "Invalid email or password.";
    } else if (error.code === "auth/too-many-requests") {
      message = "Too many failed attempts. Please try again later.";
    } else if (error.code === "auth/user-disabled") {
      message = "This account has been disabled.";
    } else {
      // For debugging - you can remove this in production
      message = `Login failed: ${error.message}`;
    }

    document.getElementById("login-output").innerText = message;
  }
});

// ✅ Handle signup
// ✅ Signup

document.getElementById("signup-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;

  const full_name = form.full_name.value.trim();
  const email = form.email.value.trim();
  const password = form.password.value;
  const bus_name = form.bus_name.value.trim();
  const bus_number = form.bus_number.value.trim();
  const bus_route = form.bus_route.value; // this is now the document ID from dropdown
  const bus_timings = form.bus_timings.value.trim();

  // Check if a route is selected
  if (!bus_route) {
    document.getElementById("signup-output").innerText = "Please select a bus route.";
    return;
  }

  try {
    console.log("Creating user account...");
    const userCredential = await auth.createUserWithEmailAndPassword(email, password);
    const user = userCredential.user;

    // Save driver info in Firestore
    await db.collection("drivers").doc(user.uid).set({
      full_name,
      email,
      bus_name,
      bus_number,
      bus_route,   // stores the document ID (e.g., route_22)
      bus_timings,
    });

    console.log("Data saved successfully");
    
    // Switch to login tab and show success
    switchTab('login');
    document.getElementById("login-output").innerText = "Signup successful! Please login.";
    document.getElementById("signup-output").innerText = ""; // clear any previous error

  } catch (error) {
    console.error("Full error:", error);
    let message = "Signup failed!";
    if (error.code === "auth/email-already-in-use") message = "Email is already registered.";
    else if (error.code === "auth/invalid-email") message = "Invalid email format.";
    else if (error.code === "auth/weak-password") message = "Password should be at least 6 characters.";
    else message = error.message;

    document.getElementById("signup-output").innerText = message;
  }
});
// Load bus routes into signup dropdown
async function loadSignupRoutes() {
  try {
    const response = await fetch("http://localhost:8000/routes");
    const routes = await response.json();

    const select = document.getElementById("bus_route");
    if (!select) return;

    select.innerHTML = '<option value="">--Select Route--</option>';

    routes.forEach(route => {
      const option = document.createElement("option");
      option.value = route.route_id;      // store the document ID
      option.textContent = `${route.route_no} → ${route.destination}`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading signup routes:", error);
  }
}

// Call this when signup page loads
document.addEventListener("DOMContentLoaded", loadSignupRoutes);


// Toast notifications utility
function showToast(title, description, type = 'info') {
  const toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    // Create toast container if it doesn't exist
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 1000;
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.style.cssText = `
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow-card);
    max-width: 300px;
    color: var(--foreground);
  `;

  toast.innerHTML = `
    <div class="toast-title" style="font-weight: bold; margin-bottom: 0.5rem;">${title}</div>
    <div class="toast-description">${description}</div>
  `;

  const container = document.getElementById('toast-container');
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3000);
}
// DRIVER PORTAL FUNCTIONALITY

// 🔹 Function to fetch and render stops for the driver's route


// ===== FETCH AND RENDER STOPS =====
async function renderDriverStops() {
  const tripsDiv = document.getElementById("driver-trip-list");
  if (!tripsDiv) return;

  tripsDiv.innerHTML = "<h2>Your trips today</h2>";

  const routeId = localStorage.getItem("selectedRouteId");
  console.log("routeId:", routeId);

  if (!routeId) {
    tripsDiv.innerHTML += "<p>No route found. Please log in again.</p>";
    return;
  }

  try {
    const res = await fetch(`/stops/${routeId}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const stops = await res.json();

    if (!stops || stops.length === 0) {
      tripsDiv.innerHTML += "<p>No stops found for this route.</p>";
      return;
    }

    currentStops = stops; // save globally
    currentStopIndex = 0;

    const ul = document.createElement("ul");
    ul.style.listStyle = "none";
    ul.style.padding = "0";
    tripsDiv.appendChild(ul);

    updateStopsView();

  } catch (err) {
    console.error("Error fetching stops:", err);
    tripsDiv.innerHTML += `<p>Error loading stops: ${err.message}</p>`;
  }
}

// ===== UPDATE STOPS UI =====
function updateStopsView() {
  const ul = document.querySelector("#driver-trip-list ul");
  if (!ul) return;

  ul.innerHTML = "";

  currentStops.forEach((stop, index) => {
    const li = document.createElement("li");
    li.textContent = stop.stop_name;
    li.style.padding = "0.5rem";
    li.style.marginBottom = "0.25rem";
    li.style.borderRadius = "var(--radius)";
    li.style.backgroundColor = index === currentStopIndex ? "var(--success)" : "var(--muted)";
    li.style.color = index === currentStopIndex ? "white" : "var(--foreground)";
    li.style.fontWeight = index === currentStopIndex ? "bold" : "normal";
    ul.appendChild(li);
  });

  if (delayMessage) delayMessage.textContent = "";
  if (delayReasonSelect) delayReasonSelect.value = "";
}

// ===== MARK STOP DEPARTED =====
async function sendStopStatus(stop, status, reason = null) {
  const routeId = localStorage.getItem("selectedRouteId");
  const driverUid = localStorage.getItem("driverUid"); // or wherever you store UID
  const timestamp = new Date().toISOString();

  const payload = {
    driver_uid: driverUid,
    route_id: routeId,
    stop_id: stop.stop_id,
    status: status,
    timestamp: timestamp
  };
  
  if (reason) payload.reason = reason;

  try {
    const res = await fetch("/driver/update-stop-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return await res.json();
  } catch (err) {
    console.error("Failed to update stop status", err);
    throw err;
  }
}

// ===== Mark Departed =====
departedBtn.addEventListener("click", async () => {
  if (currentStops.length === 0 || currentStopIndex >= currentStops.length) return;

  const stop = currentStops[currentStopIndex];
  try {
    await sendStopStatus(stop, "departed");
    showToast("Stop Departed", `Departed from ${stop.stop_name}`, "success");
    currentStopIndex++;
    if (currentStopIndex < currentStops.length) updateStopsView();
    else {
      showToast("Trip Completed", "All stops completed!", "success");
      currentStops = [];
      currentStopIndex = 0;
      document.getElementById("driver-trip-list").innerHTML = "<h2>Your trips today</h2>";
    }
  } catch { /* already logged */ }
});

// ===== Flag Delay =====
delayFlagBtn.addEventListener("click", async () => {
  const reason = delayReasonSelect.value;
  if (!reason) {
    delayMessage.textContent = "Please select a reason for the delay.";
    showToast("Selection Required", "Please select a delay reason.", "warning");
    return;
  }
  
  const stop = currentStops[currentStopIndex];
  try {
    await sendStopStatus(stop, "delayed", reason);
    delayMessage.textContent = `Delay reported: ${reason}`;
    showToast("Delay Reported", `Delay reason: ${reason}`, "warning");
  } catch { /* already logged */ }
});

// ===== SHOW DRIVER PAGE =====
function showDriverPage() {
  document.getElementById("driver-page").classList.remove("hidden");
  renderDriverStops();
}


// PASSENGER PORTAL FUNCTIONALITY

// Show specific subpage in the passenger portal
function showPassengerSubPage(page) {
  ['options', 'findBus', 'report'].forEach(p => {
    const el = document.getElementById(
      p === 'options' ? 'passenger-options-page' :
      p === 'findBus' ? 'find-bus-page' : 'report-page'
    );
    if(el) {
      if(p === page) el.classList.remove('hidden');
      else el.classList.add('hidden');
    }
  });
}
// Populate routes on page load
async function loadRoutes() {
  try {
    const response = await fetch("http://localhost:8000/routes"); 
    const routes = await response.json();

    const select = document.getElementById("find-route-select");
    select.innerHTML = '<option value="">--Choose Route--</option>';

    routes.forEach(route => {
      const option = document.createElement("option");
      option.value = route.route_id;
      option.textContent = `${route.route_no} → ${route.destination}`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading routes:", error);
  }
}

// Populate stops for selected route
async function populateFindStops() {
  const routeId = document.getElementById("find-route-select").value;
  const stopSelect = document.getElementById("find-stop-select");

  // Reset stops dropdown
  stopSelect.innerHTML = '<option value="">--Choose Stop--</option>';

  if (!routeId) return; // no route selected

  try {
    const response = await fetch(`http://localhost:8000/stops/${routeId}`);
    const stops = await response.json();

    stops.forEach(stop => {
      const option = document.createElement("option");
      option.value = stop.stop_id;
      option.textContent = stop.stop_name;
      stopSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading stops:", error);
  }
}

// Init on page load
document.addEventListener("DOMContentLoaded", () => {
  loadRoutes();
});


// Populate stops for Report based on route
async function populateReportStops() {
  const routeSelect = document.getElementById("report-route-select");
  const stopSelect = document.getElementById("report-stop-select");

  const routeId = routeSelect.value;

  // Reset stops dropdown
  stopSelect.innerHTML = '<option value="">--Choose Stop--</option>';

  if (!routeId) return; // no route selected

  try {
    const response = await fetch(`http://localhost:8000/stops/${routeId}`);
    const stops = await response.json();

    stops.forEach(stop => {
      const option = document.createElement("option");
      option.value = stop.stop_id;
      option.textContent = stop.stop_name;
      stopSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading stops for report:", error);
  }
}

// Populate report routes on page load
async function loadReportRoutes() {
  try {
    const response = await fetch("http://localhost:8000/routes");
    const routes = await response.json();

    const routeSelect = document.getElementById("report-route-select");
    routeSelect.innerHTML = '<option value="">--Choose Route--</option>';

    routes.forEach(route => {
      const option = document.createElement("option");
      option.value = route.route_id;
      option.textContent = `${route.route_no} → ${route.destination}`;
      routeSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading report routes:", error);
  }
}

// Initialize report page 
document.addEventListener("DOMContentLoaded", () => {
  loadReportRoutes();
});



async function findMyBus() {
  const stopSelect = document.getElementById('find-stop-select');
  const busListDiv = document.getElementById('bus-list');

  if (!stopSelect || !busListDiv) {
    showToast('Error', 'Required elements not found!', 'error');
    return;
  }

  const stop = stopSelect.value;
  if (!stop) {
    busListDiv.innerHTML = '<p style="color: var(--warning); padding: 1rem; text-align: center;">Please select a stop.</p>';
    return;
  }

  try {
    const res = await fetch(`/api/upcoming_trips/${stop}`);
    const buses = await res.json();

    if (buses.length === 0) {
      busListDiv.innerHTML = '<p style="color: var(--muted-foreground); padding: 1rem; text-align: center;">No upcoming buses.</p>';
      return;
    }

    // Render table of ETAs
    let html = `
      <div style="margin-top: 1rem;">
        <h3 style="margin-bottom: 1rem; color: var(--primary);">Upcoming Buses:</h3>
        <table style="width: 100%; border-collapse: collapse;">
          <tr style="background: var(--card); color: var(--primary);">
            <th style="padding: 0.5rem; text-align: left;">Trip</th>
            <th style="padding: 0.5rem;">Scheduled</th>
            <th style="padding: 0.5rem;">Predicted ETA</th>
            <th style="padding: 0.5rem;">Delay</th>
          </tr>
    `;
    buses.forEach(bus => {
      html += `
        <tr style="border-top: 1px solid var(--border);">
          <td style="padding: 0.5rem;">${bus.trip_id}</td>
          <td style="padding: 0.5rem;">${bus.scheduled_arrival}</td>
          <td style="padding: 0.5rem;">${bus.predicted_eta_time}</td>
          <td style="padding: 0.5rem; color: ${bus.predicted_delay > 0 ? 'red' : 'green'};">
            ${bus.predicted_delay > 0 ? '+' + bus.predicted_delay : 'On Time'}
          </td>
        </tr>
      `;
    });
    html += '</table></div>';
    busListDiv.innerHTML = html;

    showToast('Buses Found', `Found ${buses.length} bus(es) for ${stop}`, 'success');
  } catch (err) {
    console.error(err);
    showToast('Error', 'Failed to fetch bus info.', 'error');
  }
}

// Submit report button clicked
async function submitReport() {
  const routeSelect = document.getElementById('report-route-select');
  const stopSelect = document.getElementById('report-stop-select');
  const statusInput = document.querySelector('input[name="status-report"]:checked');

  if (!routeSelect || !stopSelect || !statusInput) {
    showToast('Form Error', 'Required form elements not found.', 'error');
    return;
  }

  const route = routeSelect.value;
  const stop = stopSelect.value;
  const status = statusInput.value;

  if (!route || !stop || !status) {
    showToast('Incomplete Form', 'Please fill out all report fields.', 'warning');
    return;
  }

  try {
    const res = await fetch('/driver/update-stop-status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        driver_uid: "passenger",   // static string
        route_id: route,
        stop_id: stop,
        status: status.toLowerCase(),
        timestamp: new Date().toISOString()
      })
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();

    showToast('Report Submitted', `Route: ${route}, Stop: ${stop}, Status: ${status}`, 'success');
  } catch (err) {
    console.error("Error submitting passenger report:", err);
    showToast('Error', 'Failed to submit report. Try again.', 'error');
  }

  // Reset form
  routeSelect.value = '';
  stopSelect.innerHTML = '<option value="">--Choose Stop--</option>';
  const onTimeRadio = document.querySelector('input[name="status-report"][value="On Time"]');
  if (onTimeRadio) onTimeRadio.checked = true;
}

// Initialize functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  renderDriverTripList();
});