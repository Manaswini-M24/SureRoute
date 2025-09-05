# train_model.py
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib  # We need this to save the model

# Create a consistent training dataset
# Let's make sure it has clear anomalies: 50 (very late) and -11 (very early)
print("Creating training data with clear anomalies...")
training_data = np.array([1, -1, 2, 0, 3, -2, 50, -11, 2, 1]).reshape(-1, 1)
print("Training Data:", training_data.flatten())

# Create and train the model with a fixed random state for reproducibility
print("Training the Isolation Forest model...")
model = IsolationForest(contamination=0.2, random_state=42)  # contamination=0.2 because we have 2 anomalies in 10 points
model.fit(training_data)

# Test the model on our target value (-50) immediately to verify it works
test_sample = np.array([[-50]])  # Very early
prediction = model.predict(test_sample)
score = model.decision_function(test_sample)

print(f"\nTest Prediction for -50: {'Anomaly' if prediction == -1 else 'Normal'}")
print(f"Anomaly Score for -50: {score[0]:.4f}")

# Save the trained model to a file
model_filename = 'trained_anomaly_model.joblib'
joblib.dump(model, model_filename)
print(f"\nModel successfully trained and saved to '{model_filename}'")