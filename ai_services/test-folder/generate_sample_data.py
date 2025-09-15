import requests
import random
import time
from datetime import datetime

# API endpoint
API_URL = "http://localhost:8000/predict_delay"

# Sample data based on your actual bus routes
sample_data = [
    # Route 51-D (Morning rush - high delays)
    {"trip_id": "BUS_51D_001", "stop_id": "r51d_s5", "scheduled_arrival": 440.0, "delay_prev_stop": 8.0, "day": "monday", "time_of_day": "morning_rush"},
    {"trip_id": "BUS_51D_001", "stop_id": "r51d_s8", "scheduled_arrival": 455.0, "delay_prev_stop": 12.0, "day": "monday", "time_of_day": "morning_rush"},
    {"trip_id": "BUS_51D_001", "stop_id": "r51d_s12", "scheduled_arrival": 475.0, "delay_prev_stop": 15.0, "day": "monday", "time_of_day": "morning_rush"},
    {"trip_id": "BUS_51D_001", "stop_id": "r51d_s15", "scheduled_arrival": 490.0, "delay_prev_stop": 18.0, "day": "monday", "time_of_day": "morning_rush"},
    
    # Route 51-D (Midday - moderate delays)
    {"trip_id": "BUS_51D_002", "stop_id": "r51d_s5", "scheduled_arrival": 620.0, "delay_prev_stop": 3.0, "day": "monday", "time_of_day": "midday"},
    {"trip_id": "BUS_51D_002", "stop_id": "r51d_s8", "scheduled_arrival": 635.0, "delay_prev_stop": 4.0, "day": "monday", "time_of_day": "midday"},
    
    # Route 51-K (Evening rush)
    {"trip_id": "BUS_51K_001", "stop_id": "r51k_s10", "scheduled_arrival": 454.0, "delay_prev_stop": 7.0, "day": "tuesday", "time_of_day": "evening_rush"},
    {"trip_id": "BUS_51K_001", "stop_id": "r51k_s15", "scheduled_arrival": 468.0, "delay_prev_stop": 10.0, "day": "tuesday", "time_of_day": "evening_rush"},
    {"trip_id": "BUS_51K_001", "stop_id": "r51k_s20", "scheduled_arrival": 484.0, "delay_prev_stop": 12.0, "day": "tuesday", "time_of_day": "evening_rush"},
    
    # Route 3-M (Morning)
    {"trip_id": "BUS_3M_001", "stop_id": "r3m_s5", "scheduled_arrival": 436.0, "delay_prev_stop": 5.0, "day": "wednesday", "time_of_day": "morning_rush"},
    {"trip_id": "BUS_3M_001", "stop_id": "r3m_s10", "scheduled_arrival": 456.0, "delay_prev_stop": 8.0, "day": "wednesday", "time_of_day": "morning_rush"},
    
    # Route 42 (Midday)
    {"trip_id": "BUS_42_001", "stop_id": "r42_s5", "scheduled_arrival": 436.0, "delay_prev_stop": 2.0, "day": "thursday", "time_of_day": "midday"},
    {"trip_id": "BUS_42_001", "stop_id": "r42_s10", "scheduled_arrival": 456.0, "delay_prev_stop": 3.0, "day": "thursday", "time_of_day": "midday"},
    
    # Route 3-B (Friday evening - high delays)
    {"trip_id": "BUS_3B_001", "stop_id": "r3b_s5", "scheduled_arrival": 436.0, "delay_prev_stop": 10.0, "day": "friday", "time_of_day": "evening_rush"},
    {"trip_id": "BUS_3B_001", "stop_id": "r3b_s8", "scheduled_arrival": 448.0, "delay_prev_stop": 15.0, "day": "friday", "time_of_day": "evening_rush"},
    
    # Route 1-A (Weekend - low delays)
    {"trip_id": "BUS_1A_001", "stop_id": "r1a_s10", "scheduled_arrival": 456.0, "delay_prev_stop": 1.0, "day": "saturday", "time_of_day": "midday"},
    {"trip_id": "BUS_1A_001", "stop_id": "r1a_s15", "scheduled_arrival": 476.0, "delay_prev_stop": 2.0, "day": "saturday", "time_of_day": "midday"},
    
    # Route 13 (Frequent service)
    {"trip_id": "BUS_13_001", "stop_id": "r13_s3", "scheduled_arrival": 608.0, "delay_prev_stop": 1.0, "day": "sunday", "time_of_day": "midday"},
    {"trip_id": "BUS_13_001", "stop_id": "r13_s6", "scheduled_arrival": 620.0, "delay_prev_stop": 2.0, "day": "sunday", "time_of_day": "midday"},
    
    # Route 22 (Long route)
    {"trip_id": "BUS_22_001", "stop_id": "r22_s8", "scheduled_arrival": 448.0, "delay_prev_stop": 6.0, "day": "monday", "time_of_day": "morning_rush"},
    {"trip_id": "BUS_22_001", "stop_id": "r22_s12", "scheduled_arrival": 484.0, "delay_prev_stop": 9.0, "day": "monday", "time_of_day": "morning_rush"},
    
    # Route 14 (College area)
    {"trip_id": "BUS_14_001", "stop_id": "r14_s6", "scheduled_arrival": 740.0, "delay_prev_stop": 4.0, "day": "tuesday", "time_of_day": "midday"},
    {"trip_id": "BUS_14_001", "stop_id": "r14_s10", "scheduled_arrival": 766.0, "delay_prev_stop": 5.0, "day": "tuesday", "time_of_day": "midday"},
    
    # Route 45 (Industrial area)
    {"trip_id": "BUS_45_001", "stop_id": "r45_s7", "scheduled_arrival": 504.0, "delay_prev_stop": 3.0, "day": "wednesday", "time_of_day": "midday"},
    {"trip_id": "BUS_45_001", "stop_id": "r45_s12", "scheduled_arrival": 544.0, "delay_prev_stop": 4.0, "day": "wednesday", "time_of_day": "midday"},
    
    # Route 44-A (Coastal route)
    {"trip_id": "BUS_44A_001", "stop_id": "r44a_s8", "scheduled_arrival": 598.0, "delay_prev_stop": 5.0, "day": "thursday", "time_of_day": "evening_rush"},
    {"trip_id": "BUS_44A_001", "stop_id": "r44a_s12", "scheduled_arrival": 614.0, "delay_prev_stop": 7.0, "day": "thursday", "time_of_day": "evening_rush"},
]

def generate_sample_data(num_samples=100):
    """Generate multiple sample data points"""
    successful = 0
    failed = 0
    
    print(f"🚌 Generating {num_samples} sample data points based on real routes...")
    print("=" * 60)
    
    for i in range(num_samples):
        # Pick random sample data
        data = random.choice(sample_data)
        
        # Add realistic variation based on time of day
        base_delay = data["delay_prev_stop"]
        if data["time_of_day"] == "morning_rush":
            variation = random.uniform(-1.0, 3.0)  # More variation in rush hour
        elif data["time_of_day"] == "evening_rush":
            variation = random.uniform(-0.5, 2.5)
        else:
            variation = random.uniform(-0.5, 1.5)  # Less variation off-peak
        
        data_with_variation = data.copy()
        data_with_variation["delay_prev_stop"] = max(0, base_delay + variation)  # No negative delays
        
        try:
            response = requests.post(API_URL, json=data_with_variation, timeout=5)
            if response.status_code == 200:
                successful += 1
                if successful % 10 == 0:  # Print progress every 10 requests
                    print(f"✅ Generated {successful} samples...")
                    print(f"   Latest: {data_with_variation['trip_id']} at {data_with_variation['stop_id']}")
            else:
                failed += 1
                print(f"❌ Failed request: {response.status_code}")
                
        except Exception as e:
            failed += 1
            print(f"❌ Error: {e}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print("=" * 60)
    print(f"🎉 Generation complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total data points: {successful}")
    
    if successful > 0:
        print("\n📈 Your AI training dataset is growing!")
        print("💡 Check your CSV file: data/training/prediction_logs.csv")
        print("🚀 You now have realistic data from multiple routes and time periods!")

def test_single_prediction():
    """Test a single prediction"""
    test_data = {
        "trip_id": "BUS_51D_001",
        "stop_id": "r51d_s5", 
        "scheduled_arrival": 440.0,
        "delay_prev_stop": 8.0,
        "day": "monday",
        "time_of_day": "morning_rush"
    }
    
    try:
        response = requests.post(API_URL, json=test_data, timeout=5)
        print(f"🧪 Single test response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Single test failed: {e}")
        return False

def show_route_stats():
    """Show statistics about the sample data"""
    print("\n📊 Sample Data Statistics:")
    print("=" * 40)
    
    routes = {}
    time_periods = {}
    days = {}
    
    for data in sample_data:
        # Count routes
        routes[data['trip_id']] = routes.get(data['trip_id'], 0) + 1
        
        # Count time periods
        time_periods[data['time_of_day']] = time_periods.get(data['time_of_day'], 0) + 1
        
        # Count days
        days[data['day']] = days.get(data['day'], 0) + 1
    
    print("Routes covered:")
    for route, count in routes.items():
        print(f"  {route}: {count} stops")
    
    print("\nTime periods:")
    for period, count in time_periods.items():
        print(f"  {period}: {count} samples")
    
    print("\nDays of week:")
    for day, count in days.items():
        print(f"  {day}: {count} samples")

if __name__ == "__main__":
    # Show what data we'll generate
    show_route_stats()
    
    # First test if API is working
    print("\n🔍 Testing API connection...")
    if test_single_prediction():
        # Generate lots of sample data
        generate_sample_data(50)  # Generate 50 samples to start
    else:
        print("❌ API is not running! Start it with: python -m uvicorn app:app --reload --port 8000")