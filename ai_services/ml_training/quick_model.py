import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def create_quick_model():
    print("🎯 Creating quick model for testing...")
    
    try:
        # Create simple synthetic data if no real data
        import numpy as np
        X = np.array([[450, 5], [460, 8], [440, 3], [470, 10], [455, 6]])
        y = np.array([5, 8, 3, 10, 6])
        
        # Train simple model
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        # Save model
        model_path = 'models/xgboost_eta_model.pkl'
        joblib.dump(model, model_path)
        
        print(f"✅ Model created and saved: {model_path}")
        print(f"✅ Model can predict: {model.predict([[450, 5]])[0]}")
        
        return model
        
    except Exception as e:
        print(f"❌ Error creating model: {e}")
        return None

if __name__ == "__main__":
    create_quick_model()