import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from api_client import get_latest, get_depth_lates
import base64

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Blind Assistance IoT Dashboard", 
    layout="wide",
    page_icon="👁️‍🦯"
)

# ---------------------- CUSTOM CSS ----------------------
st.markdown("""
<style>
    .main-header { font-size: 3rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; font-weight: 700; }
    
    /* Metric Card Styles */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; border-radius: 15px; color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); height: 150px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .metric-card h3 { font-size: 1rem; margin: 0 0 8px 0; font-weight: 600; }
    .metric-card h2 { font-size: 2rem; margin: 0 0 5px 0; font-weight: 700; }
    .metric-card p { font-size: 0.85rem; margin: 0; opacity: 0.9; }

    /* Status Styles */
    .status-moving { background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%); }
    .status-stopped { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
    
    .status-card {
        padding: 1rem; border-radius: 15px; color: white; text-align: center;
        height: 150px; display: flex; flex-direction: column; justify-content: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .status-card h2 { font-size: 1.8rem; margin: 0; font-weight: 700; }

    /* Alert Styles */
    .alert-box { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; color: #333; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .alert-high { background-color: #ffebee; border-left: 5px solid #c62828; }
    .alert-medium { background-color: #fffde7; border-left: 5px solid #f9a825; }
    .alert-low { background-color: #e8f5e8; border-left: 5px solid #2e7d32; }
    
    .camera-container { border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------- AUTO REFRESH (5 SECONDS) ----------------------
# This line triggers the rerun every 5000 milliseconds (5 seconds)
st_autorefresh(interval=5000, key="data_refresh")

# ---------------------- HEADER ----------------------
st.markdown('<div class="main-header">👁️‍🦯 Blind Assistance IoT Dashboard</div>', unsafe_allow_html=True)

# ---------------------- DATA FETCHING ----------------------
# 1. Fetch Basic Sensors (Ultrasonic, IR, Gyro)
sensor_data = get_latest()

# 2. Fetch AI Camera Data (Image + Object Detection List)
ai_data = get_depth_lates()

# Initialize variables with defaults (prevent crash if server is down)
server_online = False
distance_val = 0.0
is_moving = False
buzzer_active = False
battery_level = 88 # Placeholder default
camera_image = None
detected_objects = []
last_updated_time = datetime.now().strftime('%H:%M:%S')

# Process Sensor Data
if sensor_data and "error" not in sensor_data:
    server_online = True
    distance_val = float(sensor_data.get("distance", 0))
    movement_val = int(sensor_data.get("movement", 0))
    buzzer_val = int(sensor_data.get("buzzer", 0))
    
    is_moving = (movement_val == 1)
    buzzer_active = (buzzer_val == 1)

# Process AI/Camera Data
if ai_data and "data" in ai_data:
    inner_data = ai_data["data"]
    detected_objects = inner_data.get("objects", [])
    
    # Handle Image
    b64_img = inner_data.get("image", "")
    if b64_img:
        try:
            camera_image = base64.b64decode(b64_img)
        except:
            camera_image = None
    
    # Handle Timestamp
    db_time = inner_data.get("created_at")
    if db_time:
        last_updated_time = db_time

# ---------------------- METRICS ROW ----------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📏 Obstacle Distance</h3>
        <h2>{distance_val:.1f} cm</h2>
        <p>Ultrasonic Sensor</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    status_icon = "🏃" if is_moving else "🧍"
    status_text = "MOVING" if is_moving else "IDLE"
    bg_class = "status-moving" if is_moving else "status-stopped"
    
    st.markdown(f"""
    <div class="status-card {bg_class}">
        <h3>{status_icon} User Status</h3>
        <h2>{status_text}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Logic: If buzzer is 1, system is alerting the blind user
    alert_status = "⚠️ Vibrating" if buzzer_active else "✅ Silent"
    st.markdown(f"""
    <div class="metric-card">
        <h3>🔔 Feedback System</h3>
        <h2>{alert_status}</h2>
        <p>Haptic/Audio State</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    conn_color = "#4caf50" if server_online else "#f44336"
    conn_text = "Connected" if server_online else "Offline"
    st.markdown(f"""
    <div class="metric-card" style="background: {conn_color};">
        <h3>📡 Server Status</h3>
        <h2>{conn_text}</h2>
        <p>Last Sync: {last_updated_time}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------- MAIN DISPLAY ----------------------
left_col, right_col = st.columns([2, 1])

# --- LEFT: CAMERA FEED ---
with left_col:
    st.subheader("📷 Live Depth Analysis")
    st.markdown('<div class="camera-container">', unsafe_allow_html=True)
    
    if camera_image:
        st.image(camera_image, use_container_width=True)
    else:
        # Placeholder if no image available
        st.warning("Waiting for camera stream...")
        st.markdown("""
        <div style="height:400px; background-color:#f0f2f6; display:flex; align-items:center; justify-content:center; color:#888;">
            <h2>📵 No Video Feed</h2>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT: DYNAMIC ALERTS (FROM SERVER) ---
with right_col:
    st.subheader("🚨 Detected Objects")
    
    if not server_online:
        st.error("Server unavailable. Cannot fetch alerts.")
    elif not detected_objects:
        st.success("✅ Path is clear")
        st.caption("No identifiable objects in range.")
    else:
        # Iterate over the objects returned by get_depth_lates()
        for obj in detected_objects:
            # Safely get values with defaults
            label = obj.get("class", "Unknown Object").upper()
            depth = float(obj.get("distance", 0.0))
            
            # Determine Alert Severity based on Depth
            if depth < 0.8: # Very close (less than 80cm)
                severity_class = "alert-high"
                icon = "⛔"
                msg = "CRITICAL STOP"
            elif depth < 2.0: # Moderate distance
                severity_class = "alert-medium"
                icon = "⚠️"
                msg = "Caution Ahead"
            else: # Far away
                severity_class = "alert-low"
                icon = "ℹ️"
                msg = "Detected"

            st.markdown(f"""
            <div class="alert-box {severity_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.1rem; font-weight:bold;">{icon} {label}</span>
                    <span style="font-size:0.9rem; background:rgba(255,255,255,0.5); padding:2px 6px; border-radius:4px;">{depth:.2f} m</span>
                </div>
                <div style="margin-top:5px; font-size:0.85rem;">{msg}</div>
            </div>
            """, unsafe_allow_html=True)

# ---------------------- FOOTER / ACTIONS ----------------------
st.markdown("---")
st.markdown("#### ⚡ System Controls")
b1, b2, b3, b4 = st.columns(4)

if b1.button("Force Reload", use_container_width=True):
    st.rerun()
    
if b2.button("Test Alarm", use_container_width=True):
    st.toast("Testing local buzzer...", icon="🔔")
    
if b3.button("Toggle Night Mode", use_container_width=True):
    st.info("Switching camera mode...")

if b4.button("Emergency Call", use_container_width=True):
    st.error("Sending Emergency Alert...")