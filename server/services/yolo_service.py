from db.mongo_connection import get_mongo_db
from datetime import datetime
import json

def insert_yolo_frame(file, json_str):
    """
    Saves a frame and its detections to MongoDB.
    :param file: The binary image file from request.files
    :param json_str: The stringified JSON detections from request.form
    """
    db = get_mongo_db()
    collection = db["frames"] # We will store data in the 'frames' collection

    # 1. Parse the JSON string back into a Python list
    try:
        detections = json.loads(json_str) if json_str else []
    except json.JSONDecodeError:
        detections = []

    # 2. Read the image binary data
    image_binary = file.read()

    # 3. Create the document structure
    document = {
        "created_at": datetime.utcnow(),
        "filename": file.filename,
        "image_data": image_binary, # Storing actual image in DB
        "object_count": len(detections),
        "detections": detections    # List of all objects found
    }

    # 4. Insert into MongoDB
    result = collection.insert_one(document)
    
    return str(result.inserted_id)

def get_latest_frames(limit=5):
    """
    Retrieves the latest frames (without binary data to keep it fast).
    """
    db = get_mongo_db()
    collection = db["frames"]
    
    # Fetch latest 5, but EXCLUDE the heavy 'image_data' field for preview
    cursor = collection.find({}, {"image_data": 0}).sort("created_at", -1).limit(limit)
    
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"]) # Convert ObjectId to string
        results.append(doc)
        
    return results