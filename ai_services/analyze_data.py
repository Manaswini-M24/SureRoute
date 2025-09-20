import pandas as pd
import matplotlib.pyplot as plt
import os

def analyze_data():
    print(" ANALYZING YOUR TRAINING DATA...")
    print("=" * 50)
    
    try:
        # FIXED: Specify the full path to your CSV
        csv_path = os.path.join('sureroute-eta-predictor', 'data', 'training', 'prediction_logs.csv')
        print(f"Looking for CSV at: {csv_path}")
        
        # Load your CSV data
        df = pd.read_csv(csv_path)
        
        # Basic stats
        print(f"✅ Total records: {len(df)}")
        print(f"✅ Unique bus routes: {df['trip_id'].nunique()}")
        print(f"✅ Unique stops: {df['stop_id'].nunique()}")
        print(f"✅ Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        # Delay analysis
        print(f"\n⏰ Delay Statistics:")
        print(f"   Average delay: {df['predicted_delay'].mean():.2f} minutes")
        print(f"   Max delay: {df['predicted_delay'].max():.2f} minutes")
        print(f"   Min delay: {df['predicted_delay'].min():.2f} minutes")
        
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
            
        # Route analysis
        print(f"\n🚌 Top Routes:")
        route_counts = df['trip_id'].value_counts().head(5)
        for route, count in route_counts.items():
            print(f"   {route}: {count} records")
            
        print("\n🎉 Analysis complete! You have valuable data for ML!")
        
    except FileNotFoundError:
        print("❌ CSV file not found. Check the path!")
        print("Current working directory:", os.getcwd())
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_data()

def create_visualizations():
    """Create plots to understand data patterns"""
    try:
        df = pd.read_csv('ai_services/sureroute-eta-predictor/data/training/prediction_logs.csv')
        
        print("📈 CREATING VISUALIZATIONS...")
        
        # Plot 1: Delays by time of day
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        time_delay = df.groupby('time_of_day')['predicted_delay'].mean()
        time_delay.plot(kind='bar', color='skyblue')
        plt.title('Average Delay by Time Period')
        plt.ylabel('Delay (minutes)')
        plt.xticks(rotation=45)
        
        # Plot 2: Delays by day of week
        plt.subplot(1, 2, 2)
        day_delay = df.groupby('day')['predicted_delay'].mean()
        day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_delay = day_delay.reindex(day_order, fill_value=0)
        day_delay.plot(kind='bar', color='lightcoral')
        plt.title('Average Delay by Day of Week')
        plt.ylabel('Delay (minutes)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('delay_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Visualizations saved as 'delay_analysis.png'")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")