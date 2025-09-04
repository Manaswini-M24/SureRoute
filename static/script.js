// SureRoute Application Logic

// Global state
let currentPage = 'landing';
let driverStatus = 'on-time';
let passengerStatus = 'on-time';
let driverEta = '2 minutes to next stop';
let passengerEta = '5 minutes';

let activityLog = [
  { id: 1, timestamp: new Date(), action: 'Route started', type: 'driver' }
];
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

// Toast notifications (uses browser notification API if granted)
function showToast(title, description, type = 'info') {
  const toastContainer = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  toast.innerHTML = `
    <div class="toast-title">${title}</div>
    <div class="toast-description">${description}</div>
  `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3000);

  if (Notification.permission === 'granted') {
    new Notification(title, {
      body: description,
      icon: '/favicon.ico'
    });
  }
}

// Driver Portal functions
function updateDriverStatus(action) {
  let statusText = '';
  let actionText = '';

  if (action === 'arrived') {
    driverStatus = 'on-time';
    statusText = 'Arrived at stop';
    actionText = 'Marked as arrived at stop';
    driverEta = 'At stop';
  } else if (action === 'departed') {
    driverStatus = 'on-time';
    statusText = 'Departed from stop';
    actionText = 'Departed from stop';
    driverEta = '3 minutes to next stop';
  }

  updateDriverStatusDisplay();
  updateDriverLastUpdated();
  addActivity(actionText, 'driver');
  showToast('Status Updated', statusText, 'success');
}

function updateDriverStatusDisplay() {
  const statusElement = document.getElementById('driver-status');
  const statusConfig = getStatusConfig(driverStatus);
  statusElement.className = `status-badge ${driverStatus}`;
  statusElement.innerHTML = `
    <svg class="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      ${statusConfig.icon}
    </svg>
    <span>${statusConfig.label}</span>
  `;
}

function updateDriverLastUpdated() {
  document.getElementById('driver-last-updated').textContent = 'Just now';
}

function addActivity(action, type = 'driver') {
  const activity = {
    id: activityLog.length + 1,
    timestamp: new Date(),
    action,
    type
  };
  activityLog.unshift(activity);
  renderActivityLog();
}

function renderActivityLog() {
  const activityLogElement = document.getElementById('activity-log');
  activityLogElement.innerHTML = '';
  activityLog.slice(0, 10).forEach(activity => {
    const item = document.createElement('div');
    item.className = 'activity-item';
    const timeAgo = getTimeAgo(activity.timestamp);
    item.innerHTML = `
      <span class="activity-time">${timeAgo}</span>
      <span class="activity-text">${activity.action}</span>
      <span class="activity-type ${activity.type}">${activity.type}</span>
    `;
    activityLogElement.appendChild(item);
  });
}

// Passenger Portal functions
function reportIssue(type) {
  let title = '';
  let description = '';

  if (type === 'delay') {
    title = 'Delay Reported';
    description = 'Thank you for reporting the delay. Driver has been notified.';
    passengerStatus = 'delayed';
    passengerEta = '8 minutes';
  } else if (type === 'missed') {
    title = 'Missed Bus Reported';
    description = 'Sorry you missed the bus. Next bus ETA updated.';
    passengerStatus = 'delayed';
    passengerEta = '15 minutes';
  }

  updatePassengerStatusDisplay();
  updatePassengerEta();
  updatePassengerLastUpdated();
  addNotification(`${type === 'delay' ? 'Delay' : 'Missed bus'} reported`, 'warning');
  showToast(title, description, type === 'delay' ? 'warning' : 'error');
}

function updatePassengerStatusDisplay() {
  const statusElement = document.getElementById('passenger-status');
  const statusConfig = getStatusConfig(passengerStatus);
  statusElement.className = `status-badge ${passengerStatus}`;
  statusElement.innerHTML = `
    <svg class="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      ${statusConfig.icon}
    </svg>
    <span>${statusConfig.label}</span>
  `;
}

function updatePassengerEta() {
  document.getElementById('passenger-eta').textContent = passengerEta;
}

function updatePassengerLastUpdated() {
  document.getElementById('passenger-last-updated').textContent = 'Just now';
}

function addNotification(message, type = 'info') {
  const notification = {
    id: notifications.length + 1,
    timestamp: new Date(),
    message,
    type
  };
  notifications.unshift(notification);
  renderNotifications();
}

function renderNotifications() {
  const notificationsList = document.getElementById('notifications-list');
  notificationsList.innerHTML = '';
  notifications.slice(0, 10).forEach(notification => {
    const item = document.createElement('div');
    item.className = 'notification-item';
    const timeAgo = getTimeAgo(notification.timestamp);
    item.innerHTML = `
      <span class="notification-time">${timeAgo}</span>
      <span class="notification-text">${notification.message}</span>
    `;
    notificationsList.appendChild(item);
  });
}

// Utility functions
function getStatusConfig(status) {
  switch (status) {
    case 'on-time':
      return {
        label: 'On Time',
        icon: '<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" stroke-width="2"/><path d="m9 12 2 2 4-4" stroke-width="2"/>'
      };
    case 'delayed':
      return {
        label: 'Delayed',
        icon: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" stroke-width="2"/><path d="M12 9v4" stroke-width="2"/><path d="m12 17 .01 0" stroke-width="2"/>'
      };
    case 'early':
      return {
        label: 'Early',
        icon: '<circle cx="12" cy="12" r="10" stroke-width="2"/><polyline points="12,6 12,12 16,14" stroke-width="2"/>'
      };
    default:
      return {
        label: 'Unknown',
        icon: '<circle cx="12" cy="12" r="10" stroke-width="2"/><polyline points="12,6 12,12 16,14" stroke-width="2"/>'
      };
  }
}

function getTimeAgo(timestamp) {
  const now = new Date();
  const diff = now - timestamp;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes === 1) return '1 min ago';
  if (minutes < 60) return `${minutes} mins ago`;
  const hours = Math.floor(minutes / 60);
  if (hours === 1) return '1 hour ago';
  return `${hours} hours ago`;
}

function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}

// Simulate driver system activity
function simulateDriverUpdates() {
  setInterval(() => {
    if (currentPage === 'driver') {
      addActivity('System check completed', 'system');
    }
  }, 30000);
}

// Simulate countdown for passenger ETA
function simulatePassengerUpdates() {
  setInterval(() => {
    if (currentPage === 'passenger' && passengerStatus === 'on-time') {
      const etaMinutes = parseInt(passengerEta);
      if (etaMinutes > 1) {
        passengerEta = `${etaMinutes - 1} minutes`;
        updatePassengerEta();
      }
    }
  }, 60000);
}

// Initialize app on load
function init() {
  requestNotificationPermission();
  simulateDriverUpdates();
  simulatePassengerUpdates();
  updateDriverStatusDisplay();
  updatePassengerStatusDisplay();
  updatePassengerEta();
  renderActivityLog();
  renderNotifications();
  showPage('landing');
  console.log('SureRoute application initialized');
}

document.addEventListener('DOMContentLoaded', init);

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

// Login form submit handler (demo)
function handleLogin(event) {
  event.preventDefault();
  // Add real authentication here if needed
  showToast('Login Successful', 'Welcome back, Driver!', 'success');
  closeAccountModal();
}

// Signup form submit handler (demo)
function handleSignup(event) {
  event.preventDefault();
  // Add real signup integration here
  showToast('Signup Successful', 'Driver account created. Please log in.', 'success');
  switchTab('login');
}
