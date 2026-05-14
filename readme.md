# 👁️‍🦯 Blind Assistance IoT System

> An intelligent, real-time assistive system that combines IoT sensors, computer vision, and AI-powered depth estimation to help visually impaired individuals navigate their environment safely.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Hardware Components](#hardware-components)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [ML Module Setup](#ml-module-setup)
  - [Dashboard Setup](#dashboard-setup)
  - [ESP32 Firmware](#esp32-firmware)
- [API Reference](#api-reference)
- [Dashboard Preview](#dashboard-preview)
- [Acknowledgements](#acknowledgements)

---

## Overview

The **Blind Assistance IoT System** is a multi-component project designed to provide real-time environmental awareness to visually impaired users. The system fuses data from physical sensors (ultrasonic, PIR, buzzer) mounted on a wearable device with a camera-based AI pipeline that performs **object detection** and **metric depth estimation**, delivering actionable alerts through haptic and audio feedback.

A live **Streamlit dashboard** provides caregivers and researchers with a real-time monitoring interface displaying sensor readings, camera feeds, and detected obstacles with their distances.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER / WEARABLE                          │
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│   │  ESP32 MCU   │    │  Raspberry   │    │ Haptic / Buzzer │  │
│   │  HC-SR04     │    │  Pi Camera   │    │   Feedback      │  │
│   │  PIR Sensor  │    │  + YOLO      │    │                 │  │
│   └──────┬───────┘    └──────┬───────┘    └─────────────────┘  │
└──────────┼────────────────── ┼────────────────────────────────--┘
           │  HTTP POST        │  HTTP POST
           ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask REST API (Server)                    │
│                                                                 │
│   /api/sensor          /api/yolo          /api/depth            │
│        │                    │                   │               │
│        ▼                    ▼                   ▼               │
│   PostgreSQL DB        MongoDB (frames)   MongoDB (depth)       │
└─────────────────────────────────────────────────────────────────┘
           │
           │  HTTP GET (polling)
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ML Depth Analysis Pipeline                     │
│                                                                 │
│   Fetch frame → Apple DepthPro → Metric Depth → Upload result  │
└─────────────────────────────────────────────────────────────────┘
           │
           │  HTTP GET (auto-refresh)
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Streamlit Dashboard                           │
│   Live sensor metrics │ Camera feed │ Object alerts            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

- 🔊 **Real-time Obstacle Detection** — Ultrasonic sensor triggers haptic/buzzer feedback when obstacles are within 50 cm
- 🏃 **Motion Detection** — PIR sensor tracks user movement state (moving / idle)
- 📷 **AI Camera Pipeline** — Raspberry Pi captures frames, runs YOLO object detection, and uploads results
- 📐 **Metric Depth Estimation** — Apple's DepthPro model estimates real-world distances (in meters) for each detected object
- 🚨 **Severity Classification** — Objects categorized as Critical (<0.8 m), Caution (<2.0 m), or Detected (>2.0 m)
- 📊 **Live Dashboard** — Auto-refreshing Streamlit UI with sensor cards, camera feed, and dynamic alert panel
- 🗄️ **Dual Database** — PostgreSQL for time-series sensor data, MongoDB for image/detection storage

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Microcontroller** | ESP32 (Arduino framework) |
| **Computer Vision** | YOLO (Ultralytics), OpenCV |
| **Depth Estimation** | Apple DepthPro (HuggingFace) |
| **Backend API** | Flask, Blueprints |
| **Sensor Database** | PostgreSQL + psycopg2 |
| **Vision Database** | MongoDB + PyMongo |
| **Dashboard** | Streamlit, streamlit-autorefresh |
| **ML Framework** | PyTorch, HuggingFace Transformers |
| **Communication** | HTTP/REST, JSON, Base64 image encoding |

---

## Project Structure

```
blind-assistance-iot/
│
├── esp32/
│   ├── esp_dist_mouv_buz.ino       # ESP32 firmware (sensors + buzzer logic)
│   └── iot_dump.sql                # PostgreSQL schema and sample data
│
├── server/
│   ├── app.py                      # Flask application entry point
│   ├── db/
│   │   ├── connection.py           # PostgreSQL connection helper
│   │   └── mongo_connection.py     # MongoDB singleton connection
│   ├── routes/
│   │   ├── sensor_routes.py        # /api/sensor endpoints
│   │   ├── yolo_route.py           # /api/yolo endpoints
│   │   └── depth_route.py          # /api/depth endpoints
│   └── services/
│       ├── sensor_service.py       # Sensor DB read/write logic
│       ├── yolo_service.py         # YOLO frame storage logic
│       └── depth_servie.py         # Depth result storage/retrieval
│
├── ml-depth-pro/
│   ├── depth.py                    # Main ML inference loop
│   ├── depth_model.py              # DepthPro + YOLO model wrappers
│   ├── src/depth_pro/              # Apple DepthPro source (submodule)
│   └── get_pretrained_models.sh    # Checkpoint download script
│
├── dashboard/
│   ├── app.py                      # Streamlit dashboard
│   └── api_client.py               # HTTP client for Flask API
│
├── requierements.txt               # Python dependencies
└── README.md
```

---

## Hardware Components

| Component | Role |
|---|---|
| **ESP32** | Main microcontroller — reads sensors, sends data via Wi-Fi |
| **HC-SR04 Ultrasonic Sensor** | Measures distance to obstacles (up to ~4 m) |
| **PIR Motion Sensor** | Detects user movement |
| **Buzzer** | Haptic/audio alert when obstacle < 50 cm |
| **Raspberry Pi + Camera** | Captures video frames, runs YOLO locally |

### ESP32 Pin Mapping

| Pin | Component |
|---|---|
| GPIO 22 | HC-SR04 TRIG |
| GPIO 21 | HC-SR04 ECHO |
| GPIO 23 | PIR Signal |
| GPIO 19 | Buzzer |

---

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 14+
- MongoDB 6+
- CUDA-capable GPU (recommended for DepthPro)
- Arduino IDE (for ESP32 flashing)

---

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/blind-assistance-iot.git
cd blind-assistance-iot

# 2. Install Python dependencies
pip install -r requierements.txt

# 3. Set up PostgreSQL database
psql -U postgres -f esp32/iot_dump.sql

# 4. Start MongoDB
mongod --dbpath /your/db/path

# 5. Configure database credentials
# Edit server/db/connection.py with your PostgreSQL credentials
# Edit server/db/mongo_connection.py if using a remote MongoDB instance

# 6. Start the Flask server
cd server
python app.py
```

The API will be available at `http://localhost:5000`.

---

### ML Module Setup

```bash
cd ml-depth-pro

# 1. Create a virtual environment
conda create -n depth-pro -y python=3.9
conda activate depth-pro

# 2. Install the depth_pro package
pip install -e .

# 3. Download pretrained model checkpoints
source get_pretrained_models.sh

# 4. Start the depth analysis loop
python depth.py
```

> **Note:** The ML pipeline polls `GET /api/yolo/latest` for new frames, runs DepthPro inference, and pushes results to `POST /api/depth/upload_depth_result` automatically.

---

### Dashboard Setup

```bash
cd dashboard

# Run the Streamlit app
streamlit run app.py
```

The dashboard auto-refreshes every **5 seconds** and connects to the Flask backend at `http://localhost:5000/api`.

---

### ESP32 Firmware

1. Open `esp32/esp_dist_mouv_buz.ino` in the Arduino IDE
2. Install required libraries:
   - `WiFi.h` (built-in ESP32)
   - `HTTPClient.h` (built-in ESP32)
   - `ArduinoJson` (install via Library Manager)
3. Update Wi-Fi credentials and server IP:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   String serverUrl = "http://YOUR_SERVER_IP:5000/api/sensor";
   ```
4. Flash to your ESP32 board

---

## API Reference

### Sensor Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/sensor` | Ingest sensor reading from ESP32 |
| `GET` | `/api/sensor/latest` | Get most recent sensor row |
| `GET` | `/api/sensor/all?limit=200` | Get historical sensor data |

### YOLO / Camera Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/yolo/upload_frame` | Upload a captured frame + detections |
| `GET` | `/api/yolo/latest` | Get latest frame with detections |

### Depth Analysis Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/depth/upload_depth_result` | Save annotated depth frame + objects |
| `GET` | `/api/depth/get_latest_depth_result` | Get latest depth analysis result |

#### Example: Depth Result Response

```json
{
  "status": "success",
  "data": {
    "_id": "64a1f2...",
    "created_at": "2025-11-26T19:26:08.680Z",
    "image": "<base64_encoded_annotated_frame>",
    "object_count": 2,
    "objects": [
      { "class": "person", "distance": 1.45 },
      { "class": "car",    "distance": 3.82 }
    ]
  }
}
```

---

## Dashboard Preview

The Streamlit dashboard provides:

- **📏 Obstacle Distance** — Live ultrasonic reading in cm
- **🏃 User Status** — Moving / Idle based on PIR sensor
- **🔔 Feedback System** — Haptic/buzzer activation state
- **📡 Server Status** — Connection health + last sync timestamp
- **📷 Live Depth Feed** — Latest annotated camera frame from the ML pipeline
- **🚨 Detected Objects Panel** — Color-coded severity alerts per detected object

| Severity | Distance | Indicator |
|---|---|---|
| ⛔ Critical | < 0.8 m | Red — STOP |
| ⚠️ Caution | < 2.0 m | Yellow — Slow down |
| ℹ️ Detected | > 2.0 m | Green — Awareness |

---

## Acknowledgements

- **[Apple DepthPro](https://github.com/apple/ml-depth-pro)** — Zero-shot metric monocular depth estimation model used for real-world distance inference
- **[Ultralytics YOLO](https://github.com/ultralytics/ultralytics)** — Object detection backbone running on the edge device
- **[PyTorch Image Models (timm)](https://github.com/huggingface/pytorch-image-models)** — ViT backbone used within DepthPro
- **[DINOv2](https://github.com/facebookresearch/dinov2)** — Self-supervised vision features powering the depth encoder

---

<p align="center">
  Built with ❤️ to make the world more accessible.
</p>
