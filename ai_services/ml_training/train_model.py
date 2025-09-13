import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import joblib
import os

def train_ml_models():
    print("🤖 TRAINING ML MODELS...")
    print("=" * 50)
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "..", "sureroute-eta-predictor", "prediction_logs.csv")
        
        print(f"📁 Looking for data at: {csv_path}")
        
        if not os.path.exists(csv_path):
            print("❌ CSV file not found!")
            return None
            
        # ✅ FIX: Read CSV without headers and manually assign them
        df = pd.read_csv(csv_path, header=None)
        
        # ✅ MANUALLY SET COLUMN NAMES
        df.columns = [
            'timestamp', 'trip_id', 'stop_id', 'scheduled_arrival', 
            'delay_prev_stop', 'day', 'time_of_day', 'predicted_delay', 
            'predicted_eta', 'predicted_eta_time', 'model_version'
        ]
        
        print("✅ Columns set:", df.columns.tolist())
        print(f"📊 Total records: {len(df)}")
        
        if len(df) < 50:
            print("❌ Need at least 50 records for ML training")
            return None
            
        # Prepare features and target
        X = df[['scheduled_arrival', 'delay_prev_stop']]
        y = df['predicted_delay']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 1. BASELINE: Current rule
        baseline_pred = X_test['delay_prev_stop']
        baseline_mae = mean_absolute_error(y_test, baseline_pred)
        baseline_r2 = r2_score(y_test, baseline_pred)
        
        # 2. XGBOOST
        xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        xgb_model.fit(X_train, y_train)
        xgb_pred = xgb_model.predict(X_test)
        xgb_mae = mean_absolute_error(y_test, xgb_pred)
        xgb_r2 = r2_score(y_test, xgb_pred)
        
        # Results
        print(f"\n🎯 PERFORMANCE COMPARISON:")
        print(f"Baseline MAE: {baseline_mae:.3f} minutes | R²: {baseline_r2:.3f}")
        print(f"XGBoost MAE:  {xgb_mae:.3f} minutes | R²: {xgb_r2:.3f}")

        # ✅ FIXED: Handle division by zero
        if baseline_mae > 0:
            improvement = ((baseline_mae - xgb_mae) / baseline_mae) * 100
            print(f"Improvement:  {improvement:.1f}%")
        else:
            print("Improvement: Baseline is already perfect (0 MAE)!")
            print(f"XGBoost MAE: {xgb_mae:.3f} minutes")

        # Save model if better
        if xgb_mae <= baseline_mae:  # Also save if equal
            models_dir = os.path.join(current_dir, "models")
            os.makedirs(models_dir, exist_ok=True)
            model_path = os.path.join(models_dir, "xgboost_eta_model.pkl")
            joblib.dump(xgb_model, model_path)
            print(f"\n✅ Model saved: {model_path}")
    
            # Feature importance
            print(f"\n📈 Feature Importance:")
            for feature, importance in zip(X.columns, xgb_model.feature_importances_):
                print(f"  {feature}: {importance:.3f}")

        return xgb_model
    except Exception as e:
        print(f"❌ Error training models: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    monitor_performance()
if __name__ == "__main__":
    train_ml_models()