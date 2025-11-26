from flask import Blueprint, request, jsonify
from services.sensor_service import insert_sensor_data, get_latest_data, get_all_data

sensor_bp = Blueprint("sensor", __name__)

@sensor_bp.route("/sensor", methods=["POST"])
def post_sensor_data():
    data = request.json
    insert_sensor_data(data["distance"], data["movement"], data["buzzer"])
    return jsonify({"status": "ok"}), 200


@sensor_bp.route("/sensor/latest", methods=["GET"])
def latest_sensor():
    row = get_latest_data()
    return jsonify({
        "id": row[0],
        "timestamp": row[1],
        "distance": row[2],
        "movement": row[3],
        "buzzer": row[4]
    })


@sensor_bp.route("/sensor/all", methods=["GET"])
def all_sensor():
    limit = request.args.get("limit", 200)
    rows = get_all_data(limit)
    return jsonify([
        {
            "id": r[0],
            "timestamp": r[1],
            "distance": r[2],
            "movement": r[3],
            "buzzer": r[4]
        }
        for r in rows
    ])
