# ai_services/ml_training/auto_retrain.py
import pandas as pd
import os
import joblib
from train_model import train_ml_models  # Import your training function
from monitor_performance import monitor_performance
import time
from datetime import datetime

class AutoRetrainer:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(self.current_dir, "..", "sureroute-eta-predictor", "prediction_logs.csv")
        self.last_record_count = 0
        self.retrain_interval = 500  # Retrain every 500 new records
        self.last_retrain_time = 0
        
    def check_for_new_data(self):
        """Check if enough new data is available for retraining"""
        try:
            if not os.path.exists(self.csv_path):
                return False
                
            df = pd.read_csv(self.csv_path, header=None)
            current_records = len(df)
            
            print(f"📊 Records: {current_records} | Last: {self.last_record_count} | Needed: {self.retrain_interval}")
            
            # Check if enough new records
            if current_records - self.last_record_count >= self.retrain_interval:
                print("🔄 Enough new data for retraining!")
                return True
                
            # Also retrain if 7 days passed (even without enough data)
            current_time = time.time()
            if current_time - self.last_retrain_time > 7 * 24 * 3600:  # 7 days
                print("🔄 Weekly retraining triggered")
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ Error checking data: {e}")
            return False
    
    def auto_retrain(self):
        """Automatically retrain model if conditions are met"""
        if self.check_for_new_data():
            print("🚀 Starting auto-retraining...")
            
            # Backup current model
            self.backup_current_model()
            
            # Retrain
            model = train_ml_models()
            if model:
                self.last_record_count = self.get_current_record_count()
                self.last_retrain_time = time.time()
                print("✅ Auto-retraining completed successfully!")
                
                # Generate performance report
                monitor_performance()
                
                return True
        return False
    
    def backup_current_model(self):
        """Backup the current model before retraining"""
        try:
            model_path = os.path.join(self.current_dir, "models", "xgboost_eta_model.pkl")
            if os.path.exists(model_path):
                backup_dir = os.path.join(self.current_dir, "model_backups")
                os.makedirs(backup_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(backup_dir, f"xgboost_eta_model_{timestamp}.pkl")
                
                joblib.dump(joblib.load(model_path), backup_path)
                print(f"✅ Model backed up: {backup_path}")
                
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    def get_current_record_count(self):
        """Get current number of records in CSV"""
        try:
            df = pd.read_csv(self.csv_path, header=None)
            return len(df)
        except:
            return 0
    
    def run_continuous_monitoring(self, check_interval=3600):
        """Run continuous monitoring (every hour)"""
        print("🔍 Starting continuous monitoring...")
        while True:
            print(f"\n⏰ Check at {datetime.now()}")
            self.auto_retrain()
            print(f"😴 Sleeping for {check_interval//3600} hours...")
            time.sleep(check_interval)

def main():
    retrainer = AutoRetrainer()
    
    # Run once immediately
    retrainer.auto_retrain()
    
    # Uncomment for continuous monitoring (runs as a service)
    # retrainer.run_continuous_monitoring()

if __name__ == "__main__":
    main()