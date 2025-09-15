import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import joblib
import os
from monitor_performance import monitor_performance  # ✅ FIXED: Added import

def encode_categorical_features(df):
    """Encode categorical features for ML (matching app.py encoding)"""
    
    # Day encoding - exactly matching app.py
    day_map = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 
               'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    df['day_encoded'] = df['day'].map(day_map).fillna(1)
    
    # Time of day encoding - exactly matching app.py
    time_map = {'morning': 1, 'afternoon': 2, 'evening': 3, 'night': 4}
    df['time_encoded'] = df['time_of_day'].map(time_map).fillna(2)
    
    return df

def train_ml_models():
    print("🤖 TRAINING ML MODELS WITH 4 FEATURES...")
    print("=" * 60)
    
    try:
        # Get the correct path dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "..", "sureroute-eta-predictor", "prediction_logs.csv")
        
        print(f"📁 Looking for data at: {csv_path}")
        print(f"📁 File exists: {os.path.exists(csv_path)}")
        
        if not os.path.exists(csv_path):
            print("❌ CSV file not found!")
            print("Please generate data first by running:")
            print("python generate_sample_data.py 100")
            return None
            
        # Try to read CSV with proper header handling
        try:
            df = pd.read_csv(csv_path)
            print(f"📊 CSV read successfully with headers")
        except:
            # Fallback: read without headers and assign column names
            df = pd.read_csv(csv_path, header=None)
            df.columns = [
                'timestamp', 'trip_id', 'stop_id', 'scheduled_arrival', 
                'delay_prev_stop', 'day', 'time_of_day', 'predicted_delay', 
                'predicted_eta', 'predicted_eta_time', 'model_version'
            ]
            print(f"📊 CSV read with manual column assignment")
        
        print(f"📊 Total records: {len(df)}")
        print(f"📊 Columns: {list(df.columns)}")
        
        if len(df) < 50:
            print("❌ Need at least 50 records for ML training")
            print(f"Current records: {len(df)}")
            print("Generate more data with: python generate_sample_data.py 100")
            return None
        
        # ✅ ENCODE CATEGORICAL FEATURES
        df = encode_categorical_features(df)
        print(f"✅ Features encoded successfully")
        
        # ✅ USE ALL 4 FEATURES (same order as app.py)
        feature_columns = ['scheduled_arrival', 'delay_prev_stop', 'day_encoded', 'time_encoded']
        
        # Verify all features exist
        missing_features = [col for col in feature_columns if col not in df.columns]
        if missing_features:
            print(f"❌ Missing features: {missing_features}")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        X = df[feature_columns]
        y = df['predicted_delay']
        
        print(f"✅ Feature matrix shape: {X.shape}")
        print(f"✅ Target vector shape: {y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print(f"📊 Training set: {X_train.shape[0]} samples")
        print(f"📊 Test set: {X_test.shape[0]} samples")
        
        # 1. BASELINE: Current rule-based prediction
        baseline_pred = X_test['delay_prev_stop']
        baseline_mae = mean_absolute_error(y_test, baseline_pred)
        baseline_r2 = r2_score(y_test, baseline_pred)
        
        # 2. XGBOOST with all 4 features
        print(f"\n🚀 Training XGBoost model...")
        xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42,
            verbosity=0  # Reduce XGBoost output
        )
        xgb_model.fit(X_train, y_train)
        xgb_pred = xgb_model.predict(X_test)
        xgb_mae = mean_absolute_error(y_test, xgb_pred)
        xgb_r2 = r2_score(y_test, xgb_pred)
        
        # ✅ RESULTS COMPARISON
        print(f"\n🎯 PERFORMANCE COMPARISON:")
        print(f"Features used: {feature_columns}")
        print(f"Training samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        print(f"-" * 50)
        print(f"Baseline (rule-based) MAE: {baseline_mae:.3f} minutes | R²: {baseline_r2:.3f}")
        print(f"XGBoost (4-features) MAE:  {xgb_mae:.3f} minutes | R²: {xgb_r2:.3f}")

        # Calculate improvement safely
        if baseline_mae > 0:
            improvement = ((baseline_mae - xgb_mae) / baseline_mae) * 100
            print(f"Improvement: {improvement:.1f}%")
        else:
            print("Improvement: Baseline MAE is 0 - cannot calculate percentage")
            print(f"XGBoost absolute MAE: {xgb_mae:.3f} minutes")

        # ✅ SAVE MODEL IF BETTER OR EQUAL
        model_saved = False
        if xgb_mae <= baseline_mae:
            try:
                # Save to correct models directory 
                models_dir = os.path.join(current_dir, "..", "sureroute-eta-predictor", "models")
                os.makedirs(models_dir, exist_ok=True)
                model_path = os.path.join(models_dir, "xgboost_eta_model.pkl")
                
                joblib.dump(xgb_model, model_path)
                model_saved = True
                print(f"\n✅ Model saved: {model_path}")
                print(f"📁 Model file size: {os.path.getsize(model_path) / 1024:.1f} KB")
        
                # ✅ FEATURE IMPORTANCE ANALYSIS
                print(f"\n📈 Feature Importance Analysis:")
                feature_importance = list(zip(feature_columns, xgb_model.feature_importances_))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                for feature, importance in feature_importance:
                    print(f"  {feature:20}: {importance:.3f}")
                    
                # Save feature importance to file
                importance_file = os.path.join(models_dir, "feature_importance.txt")
                with open(importance_file, 'w') as f:
                    f.write("Feature Importance Analysis\n")
                    f.write("=" * 30 + "\n")
                    for feature, importance in feature_importance:
                        f.write(f"{feature}: {importance:.3f}\n")
                
                print(f"📝 Feature importance saved: {importance_file}")
                
            except Exception as save_error:
                print(f"❌ Error saving model: {save_error}")
                model_saved = False
        else:
            print(f"\n❌ XGBoost didn't improve over baseline")
            print(f"   Baseline MAE: {baseline_mae:.3f}")
            print(f"   XGBoost MAE:  {xgb_mae:.3f}")
            print(f"   Model not saved")

        # ✅ TRAINING SUMMARY
        print(f"\n📋 TRAINING SUMMARY:")
        print(f"   Dataset: {len(df)} total records")
        print(f"   Features: {len(feature_columns)} (enhanced from 2 to 4)")
        print(f"   Model type: XGBoost Regressor")
        print(f"   Performance: {'✅ Improved' if xgb_mae < baseline_mae else '📊 Equal' if xgb_mae == baseline_mae else '❌ No improvement'}")
        print(f"   Model saved: {'✅ Yes' if model_saved else '❌ No'}")
        print(f"   Ready for production: {'✅ Yes' if model_saved else '⚠️  Using fallback'}")
        
        return xgb_model
        
    except Exception as e:
        print(f"❌ Error training models: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Starting SureRoute ML Training Pipeline...")
    model = train_ml_models()
    
    if model:
        print(f"\n🔍 Running performance monitoring...")
        try:
            monitor_performance()  # ✅ FIXED: Now this will work
            print(f"✅ Training pipeline completed successfully!")
        except Exception as monitor_error:
            print(f"⚠️  Training completed but monitoring failed: {monitor_error}")
    else:
        print(f"❌ Training pipeline failed!")
    
    print(f"\n{'='*60}")
    print(f"🎯 SureRoute ML Training Complete!")
    print(f"{'='*60}")