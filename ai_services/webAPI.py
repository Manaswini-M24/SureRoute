from flask import Flask, request, jsonify
import numpy as np
import joblib

app = Flask(__name__)

# Load the pre-trained model when the server starts
print("Loading pre-trained anomaly detection model...")
model = joblib.load('trained_anomaly_model.joblib')
print("Model loaded successfully!")

# === DIAGNOSTIC TEST ===
print("=== DIAGNOSTIC: Testing loaded model ===")
test_value = -50
test_sample = np.array([[test_value]])
prediction = model.predict(test_sample)
score = model.decision_function(test_sample)
print(f"Value: {test_value} -> Prediction: {'Anomaly' if prediction == -1 else 'Normal'} | Score: {score[0]}")
print("=== DIAGNOSTIC END ===")

@app.route('/predict_delay', methods=['POST'])
def predict_delay():
    """
    API Endpoint that takes a JSON object with 'scheduled' and 'actual' time,
    and returns the AI's analysis.
    """
    # Get the JSON data sent from the frontend
    data = request.get_json()
    scheduled = data.get('scheduled_time')
    actual = data.get('actual_time')

    # Calculate the difference
    time_difference = actual - scheduled

    # Use the pre-loaded model for prediction
    anomaly_score = model.decision_function([[time_difference]])[0]
    is_anomaly = model.predict([[time_difference]])[0]

    # Interpret the result
    status = 'Anomaly' if is_anomaly == -1 else 'Normal'
    detailed_status = 'On Time'
    if status == 'Anomaly':
        detailed_status = 'Likely Delayed' if time_difference > 5 else 'Likely Early'

    # Send the result back as JSON
    return jsonify({
        'scheduled_time': scheduled,
        'actual_time': actual,
        'time_difference': time_difference,
        'anomaly_score': anomaly_score,
        'status': status,
        'detailed_status': detailed_status
    })

if __name__ == '__main__':
    app.run(debug=True)