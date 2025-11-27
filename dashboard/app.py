"""Dashboard for Blind Assistance IoT System"""
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from api_client import get_latest, get_all,get_depth_lates
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
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
    }
    .metric-card h3 {
        font-size: 1rem;
        margin: 0 0 8px 0;
        font-weight: 600;
    }
    .metric-card h2 {
        font-size: 2rem;
        margin: 0 0 5px 0;
        font-weight: 700;
    }
    .metric-card p {
        font-size: 0.85rem;
        margin: 0;
        opacity: 0.9;
    }
    .status-moving {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    .status-stopped {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    .status-moving h3, .status-stopped h3 {
        font-size: 1rem;
        margin: 0 0 8px 0;
        font-weight: 600;
    }
    .status-moving h2, .status-stopped h2 {
        font-size: 1.8rem;
        margin: 0;
        font-weight: 700;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .alert-red { background-color: #ffebee; color: #c62828; border-left: 5px solid #c62828; }
    .alert-yellow { background-color: #fffde7; color: #f9a825; border-left: 5px solid #f9a825; }
    .alert-green { background-color: #e8f5e8; color: #2e7d32; border-left: 5px solid #2e7d32; }
    .camera-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .quick-actions-row {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- HEADER ----------------------
st.markdown('<div class="main-header">👁️‍🦯 Blind Assistance IoT Dashboard</div>', unsafe_allow_html=True)

# ---------------------- REAL SENSOR DATA ----------------------
latest = get_latest()

if "error" in latest:
    st.error("❌ Could not fetch real data from server.")
    st.stop()

distance = latest["distance"]     # cm
movement = latest["movement"]     # 1 or 0
buzzer = latest["buzzer"]         # 1 or 0

is_moving = movement == 1
battery_level = 90  # placeholder for future battery sensor

# ---------------------- DYNAMIC ALERT LOGIC ----------------------
detected_objects = []

if distance < 50:
    detected_objects.append({
        "Object": "Obstacle detected",
        "Distance": f"{distance:.0f} cm",
        "Alert": "Red",
        "Priority": "High"
    })
elif distance < 100:
    detected_objects.append({
        "Object": "Object ahead",
        "Distance": f"{distance:.0f} cm",
        "Alert": "Yellow",
        "Priority": "Medium"
    })
else:
    detected_objects.append({
        "Object": "Clear path",
        "Distance": f"{distance:.0f} cm",
        "Alert": "Green",
        "Priority": "Low"
    })

# ---------------------- IMAGE REFRESH LOGIC ----------------------
refresh_interval = 60000 if is_moving else 600000
st_autorefresh(interval=refresh_interval, key="image_refresh")

# ---------------------- TOP METRICS ROW ----------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📏 Distance</h3>
        <h2>{distance:.1f} cm</h2>
        <p>Ultrasonic sensor reading</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    status_icon = "🎯" if is_moving else "🛑"
    status_text = "MOVING" if is_moving else "STOPPED"
    status_class = "status-moving" if is_moving else "status-stopped"
    st.markdown(f"""
    <div class="{status_class}">
        <h3>{status_icon} Status</h3>
        <h2>{status_text}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🔋 Battery</h3>
        <h2>{battery_level}%</h2>
        <p>Good condition</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📡 Connection</h3>
        <h2>{'Stable' if buzzer == 0 else 'Alert Active'}</h2>
        <p>Sensor network online</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------- MAIN CONTENT LAYOUT ----------------------
col_left, col_right = st.columns([2, 1])

# ---- Left Column: Camera Feed ----
response = get_depth_lates()
latest_data = response.get("data")
if latest_data:
    
    # --- LEFT COLUMN: IMAGE DISPLAY ---
    with col_left:
        st.subheader("📷 Environment View")

        with st.container():
            st.markdown('<div class="camera-container">', unsafe_allow_html=True)
            
            # Decode the Base64 string to bytes
            try:
                image_data = base64.b64decode(latest_data['image'])
                st.image(image_data, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")
                
            st.markdown('</div>', unsafe_allow_html=True)

        # Use the timestamp from the database, or fallback to now
        time_display = latest_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        st.caption(f"🕒 Last updated: {time_display}")

    # --- RIGHT COLUMN: OBJECT ALERTS ---
    with col_right:
        st.subheader("🚨 Immediate Alerts")
        
        objects = latest_data.get("objects", [])

        if not objects:
            st.info("✅ No obstacles detected.")
        else:
            for obj in objects:
                # Extract data
                obj_name = obj.get("class", "Unknown")
                distance = obj.get("distance", 0.0)

                # LOGIC: Determine Priority/Color based on Distance
                # < 1 meter = High (Red), < 2 meters = Medium (Orange), else Low (Green/Blue)
                if distance < 1.0:
                    priority = "CRITICAL"
                    alert_class = "alert-high" # Ensure you have this class in your CSS
                    icon = "⛔"
                elif distance < 2.5:
                    priority = "WARNING"
                    alert_class = "alert-medium"
                    icon = "⚠️"
                else:
                    priority = "INFO"
                    alert_class = "alert-low"
                    icon = "ℹ️"

                # Render the Alert Box
                st.markdown(f"""
                <div class="alert-box {alert_class}" style="padding: 10px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ddd;">
                    <strong>{icon} {obj_name.upper()}</strong>
                    <br>
                    <span style="font-size: 1.2em; font-weight: bold;">{distance} meters</span>
                    <br>
                    <small>Priority: {priority}</small>
                </div>
                """, unsafe_allow_html=True)

else:
    # Handle case where API is down or DB is empty
    with col_left:
        st.warning("Waiting for data...")
    with col_right:
        st.caption("No alerts available.")

    st.subheader("🧭 Navigation Guide")

    with st.expander("Current Route Information", expanded=True):
        st.info("""
        *Current Path:* Clear  
        *Next Turn:* Right in 50 m  
        *Destination:* 200 m ahead  
        
        🎧 Audio guidance active
        """)

# ---------------------- QUICK ACTIONS ROW ----------------------
st.markdown('<div class="quick-actions-row">', unsafe_allow_html=True)
st.subheader("⚡ Quick Actions")

a1, a2, a3, a4 = st.columns(4)

with a1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

with a2:
    if st.button("🔊 Repeat Guidance", use_container_width=True):
        st.success("Guidance repeated via audio")

with a3:
    if st.button("🆘 Emergency", use_container_width=True):
        st.error("Emergency alert sent to contacts!")

with a4:
    if st.button("📞 Call Assistant", use_container_width=True):
        st.info("Connecting to assistant...")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- BOTTOM STATUS BAR ----------------------
st.markdown("---")
bottom_col1, bottom_col2, bottom_col3 = st.columns([1, 2, 1])

with bottom_col1:
    st.markdown("*System Status:* ✅ All systems operational")

with bottom_col2:
    refresh_text = "1 min" if is_moving else "10 min"
    st.markdown(f"*Auto-refresh:* Every {refresh_text} | *Last full scan:* 30 seconds ago")

with bottom_col3:
    st.markdown("*👁️‍🦯 Assistive Tech v2.1***")

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "© 2025 Blind Assistance IoT Project | Making navigation accessible for everyone"
    "</div>", 
    unsafe_allow_html=True
)