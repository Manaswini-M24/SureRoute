# debug_path.py (create in ml_training folder)
import os

print("🔍 DEBUGGING FILE PATHS...")
print("=" * 50)

current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")

# Test multiple possible paths
possible_paths = [
    os.path.join(current_dir, "..", "..", "sureroute-eta-predictor", "prediction_logs.csv"),
    os.path.join(current_dir, "..", "..", "sureroute-eta-predictor", "data", "training", "prediction_logs.csv"),
    "../sureroute-eta-predictor/prediction_logs.csv",
    "../../sureroute-eta-predictor/prediction_logs.csv"
]

for i, path in enumerate(possible_paths):
    exists = os.path.exists(path)
    print(f"\nPath {i+1}: {path}")
    print(f"Exists: {exists}")
    if exists:
        print(f"Size: {os.path.getsize(path)} bytes")
        # Try to read a line
        try:
            with open(path, 'r') as f:
                first_line = f.readline().strip()
                print(f"First line: {first_line}")
        except Exception as e:
            print(f"Read error: {e}")

print("\n🔍 LISTING FILES IN sureroute-eta-predictor:")
sureroute_dir = os.path.join(current_dir, "..", "..", "sureroute-eta-predictor")
if os.path.exists(sureroute_dir):
    for file in os.listdir(sureroute_dir):
        if file.endswith('.csv'):
            print(f"Found CSV: {file}")

print("📊 Checking CSV columns...")
print(f"DataFrame columns: {df.columns.tolist()}")
print(f"First few rows:")
print(df.head())