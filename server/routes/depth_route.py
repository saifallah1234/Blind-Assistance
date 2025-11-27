from flask import Blueprint, request, jsonify
# FIX: 'depth_service' instead of 'depth_servie'
from services.depth_servie import insert_depth_result 

depth_bp = Blueprint('depth_bp', __name__)

@depth_bp.route("/upload_depth_result", methods=["POST"])
def upload_depth_result():
    try:
        # 1. Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # 2. Validate keys
        if 'image' not in data or 'objects' not in data:
            return jsonify({"error": "Missing 'image' or 'objects' fields"}), 400

        # 3. Save to MongoDB
        inserted_id = insert_depth_result(data)

        return jsonify({
            "status": "success", 
            "id": inserted_id,
            "message": "Depth analysis saved to MongoDB"
        }), 200

    except Exception as e:
        print(f"Error in upload_depth_result: {e}")
        return jsonify({"error": str(e)}), 500