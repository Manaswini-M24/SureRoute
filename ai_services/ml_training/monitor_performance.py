# ai_services/ml_training/monitor_performance.py
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import os
from datetime import datetime

def monitor_performance():
    print("📊 MONITORING MODEL PERFORMANCE")
    print("=" * 50)
    
    try:
        # Get data path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "..", "sureroute-eta-predictor", "prediction_logs.csv")
        
        if not os.path.exists(csv_path):
            print("❌ No data found for monitoring")
            return
        
        df = pd.read_csv(csv_path, header=None)
        df.columns = [
            'timestamp', 'trip_id', 'stop_id', 'scheduled_arrival', 
            'delay_prev_stop', 'day', 'time_of_day', 'predicted_delay', 
            'predicted_eta', 'predicted_eta_time', 'model_version'
        ]
        
        print(f"📈 Dataset Overview:")
        print(f"   Total records: {len(df):,}")
        print(f"   Unique routes: {df['trip_id'].nunique()}")
        print(f"   Unique stops: {df['stop_id'].nunique()}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        # Basic statistics
        print(f"\n📊 Delay Statistics:")
        print(f"   Avg predicted delay: {df['predicted_delay'].mean():.2f} min")
        print(f"   Max predicted delay: {df['predicted_delay'].max():.2f} min")
        print(f"   Min predicted delay: {df['predicted_delay'].min():.2f} min")
        
        # Time period analysis
        print(f"\n🌅 Time Period Distribution:")
        time_counts = df['time_of_day'].value_counts()
        for period, count in time_counts.items():
            print(f"   {period}: {count} records")
        
        # Day analysis
        print(f"\n📅 Day Distribution:")
        day_counts = df['day'].value_counts()
        for day, count in day_counts.items():
            print(f"   {day}: {count} records")
        
        # Data quality checks
        print(f"\n✅ Data Quality Checks:")
        print(f"   Missing values: {df.isnull().sum().sum()}")
        print(f"   Duplicate records: {df.duplicated().sum()}")
        
        # When you have actual delays (future enhancement)
        if 'actual_delay' in df.columns:
            mae = mean_absolute_error(df['actual_delay'], df['predicted_delay'])
            r2 = r2_score(df['actual_delay'], df['predicted_delay'])
            print(f"\n🎯 Model Performance:")
            print(f"   MAE: {mae:.2f} minutes")
            print(f"   R² Score: {r2:.3f}")
        
        # Save report
        report_path = os.path.join(current_dir, "performance_report.txt")
        with open(report_path, 'w') as f:
            f.write(f"Performance Report - {datetime.now()}\n")
            f.write(f"Total records: {len(df)}\n")
            f.write(f"Unique routes: {df['trip_id'].nunique()}\n")
            f.write(f"Average delay: {df['predicted_delay'].mean():.2f} min\n")
        
        print(f"\n📝 Report saved: {report_path}")
        
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        import traceback
        traceback.print_exc()

def plot_trends():
    """Create visualizations of data trends"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "..", "sureroute-eta-predictor", "prediction_logs.csv")
        
        df = pd.read_csv(csv_path, header=None)
        df.columns = [
            'timestamp', 'trip_id', 'stop_id', 'scheduled_arrival', 
            'delay_prev_stop', 'day', 'time_of_day', 'predicted_delay', 
            'predicted_eta', 'predicted_eta_time', 'model_version'
        ]
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        # Create plots
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Delays by hour
        plt.subplot(2, 2, 1)
        df.groupby('hour')['predicted_delay'].mean().plot(kind='bar')
        plt.title('Average Delay by Hour of Day')
        plt.xlabel('Hour')
        plt.ylabel('Delay (minutes)')
        
        # Plot 2: Delays by time category
        plt.subplot(2, 2, 2)
        df.groupby('time_of_day')['predicted_delay'].mean().plot(kind='bar')
        plt.title('Average Delay by Time Category')
        plt.xlabel('Time Category')
        plt.ylabel('Delay (minutes)')
        plt.xticks(rotation=45)
        
        # Plot 3: Records by day
        plt.subplot(2, 2, 3)
        df['day'].value_counts().plot(kind='bar')
        plt.title('Records by Day of Week')
        plt.xlabel('Day')
        plt.ylabel('Number of Records')
        plt.xticks(rotation=45)
        
        # Plot 4: Delay distribution
        plt.subplot(2, 2, 4)
        df['predicted_delay'].hist(bins=20)
        plt.title('Delay Distribution')
        plt.xlabel('Delay (minutes)')
        plt.ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(os.path.join(current_dir, 'performance_dashboard.png'))
        print("✅ Dashboard saved: performance_dashboard.png")
        
    except Exception as e:
        print(f"❌ Plotting error: {e}")

if __name__ == "__main__":
    monitor_performance()
    plot_trends()