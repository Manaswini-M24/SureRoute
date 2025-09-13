# 🚌 SureRoute ETA Prediction AI Service

A production-ready FastAPI service that predicts bus arrival times using machine learning. Deployed on Hugging Face Spaces with real-time data collection for continuous model improvement.

## 🌟 Features

- **Real-time ETA Prediction**: Rule-based and ML-powered arrival time predictions
- **Automated Data Collection**: Built-in data logging for continuous ML training
- **Production Deployment**: Live on Hugging Face with Docker containerization
- **Professional Backup System**: Automated data protection and recovery
- **Monitoring Dashboard**: Performance tracking and analytics

## 🚀 Live Deployment

**API Base URL:** `https://megha-277-sureroute-eta-predictor.hf.space`

### 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status and health |
| `/health` | GET | System health check |
| `/predict_delay` | POST | Predict bus delay and ETA |
| `/data_stats` | GET | Data collection statistics |
| `/system_status` | GET | Comprehensive system metrics |
| `/view_data` | GET | View collected training data |

### 🔌 Quick Start

```bash
# Test prediction with curl
curl -X POST "https://megha-277-sureroute-eta-predictor.hf.space/predict_delay" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": "BUS_51D_001",
    "stop_id": "r51d_s5",
    "scheduled_arrival": 450.0,
    "delay_prev_stop": 5.0,
    "day": "monday", 
    "time_of_day": "morning_rush"
  }'