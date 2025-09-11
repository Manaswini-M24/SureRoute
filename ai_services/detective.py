# detective.py
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

# This is our "AI Detective" model. We're using one called Isolation Forest.
# It's good at spotting things that are different from the norm (like a very late bus).
model = IsolationForest(contamination=0.1)  # We expect about 10% of events to be anomalies

# Let's create some SIMULATED data to play with.
# In a real project, you would load this from a database.
print("Creating sample bus data...")
data = {
    'scheduled_time': [10, 20, 30, 40, 50, 100, 110, 120, 130, 140],  # Scheduled departure times (e.g., 10:00, 10:20)
    'actual_time': [11, 19, 32, 41, 49, 50, 115, 119, 135, 138]       # Actual departure times
}
df = pd.DataFrame(data)

# Calculate the delay (or earliness) in minutes
df['time_difference'] = df['actual_time'] - df['scheduled_time']
print("Data with calculated delay:")
print(df)
print("\n")

# We need to "train" our detective on what normal data looks like.
# We use the 'time_difference' as the feature to examine.
print("Training the AI model...")
model.fit(df[['time_difference']])

# Now, let's ask the model to predict if each data point is normal (-1) or an anomaly (1).
df['anomaly_score'] = model.decision_function(df[['time_difference']])
df['is_anomaly'] = model.predict(df[['time_difference']])

# Let's make the output easier to read.
df['status'] = np.where(df['is_anomaly'] == -1, 'Anomaly', 'Normal')
# Let's interpret the anomaly further based on the time difference
df['detailed_status'] = np.where(
    df['is_anomaly'] == -1,
    np.where(df['time_difference'] > 5, 'Likely Delayed', 'Likely Early'),
    'On Time'
)

print("Analysis Results:")
print(df[['scheduled_time', 'actual_time', 'time_difference', 'anomaly_score', 'status', 'detailed_status']])