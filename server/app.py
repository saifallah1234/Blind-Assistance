from flask import Flask
from routes.sensor_routes import sensor_bp # Assuming you still have this
from routes.yolo_route import yolo_bp
from routes.depth_route import depth_bp

app = Flask(__name__)

# Register the blueprints
app.register_blueprint(sensor_bp, url_prefix="/api")
app.register_blueprint(yolo_bp, url_prefix="/api/yolo") 
app.register_blueprint(depth_bp, url_prefix="/api/depth") 

# NOTE: The full URL for the Pi will be: /api/yolo/upload_frame

if __name__ == "__main__":
    # HOST 0.0.0.0 is critical for the Pi to connect
    print("🚀 MongoDB API running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)