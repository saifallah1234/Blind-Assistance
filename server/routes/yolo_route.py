from flask import Blueprint, request, jsonify
from services.yolo_service import insert_yolo_frame, get_latest_frames

yolo_bp = Blueprint("yolo", __name__)

@yolo_bp.route("/upload_frame", methods=["POST"])
def upload_frame():
    try:
        # Check if file part exists
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        json_data = request.form.get('json_data')

        # Call service to save to MongoDB
        inserted_id = insert_yolo_frame(file, json_data)

        return jsonify({
            "status": "success", 
            "id": inserted_id,
            "message": "Frame and data saved to MongoDB"
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@yolo_bp.route("/latest", methods=["GET"])
def get_latest():
    data = get_latest_frames()
    return jsonify(data), 200