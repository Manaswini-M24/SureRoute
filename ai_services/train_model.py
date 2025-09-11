# train_model_pro.py
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

print("Creating realistic training data...")
# Let's simulate 1000 bus arrivals. Most are within +/- 3 minutes of schedule.
# We'll create a strong "normal" pattern.
np.random.seed(42)  # For absolute reproducibility

# Generate 980 normal data points (slightly early or late)
normal_data = np.random.normal(0, 1.5, 980)  # Mean 0, Std Dev 1.5 minutes

# Now, add 20 GLARING anomalies (very early or very late)
anomalies = np.array([-25, -18, 35, 40, -50, 55, -12, 60, -35, 47, -22, 30, -45, 52, 15, -22, 48, -40, 60, -15])

# Combine them into our full training set
training_data = np.concatenate((normal_data, anomalies))
training_data = training_data.reshape(-1, 1) # Reshape for the model

print(f"Created training set with {len(normal_data)} normal records and {len(anomalies)} anomalies.")
print(f"Anomalies in training set: {anomalies}")

# Create and train the model
print("\nTraining the Isolation Forest model...")
model = IsolationForest(contamination=len(anomalies)/len(training_data), random_state=42)
model.fit(training_data)

# TEST THE MODEL AGGRESSIVELY
print("\n--- Testing the Model ---")
test_values = [-50, -11, -1, 0, 2, 50, 5] # Let's test a range

for val in test_values:
    test_sample = np.array([[val]])
    prediction = model.predict(test_sample)
    score = model.decision_function(test_sample)
    print(f"Value: {val:3} -> Prediction: {'Anomaly' if prediction == -1 else 'Normal':6} | Score: {score[0]:7.3f}")

# Save the trained model to a file
model_filename = 'trained_anomaly_model.joblib'
joblib.dump(model, model_filename)
print(f"\n✅ Model successfully trained and saved to '{model_filename}'")