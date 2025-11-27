import base64
from sqlite3 import Binary
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

def get_latest_frames(limit=1):
    """
    Retrieves the latest frames and converts binary image data to Base64 strings.
    """
    db = get_mongo_db()
    collection = db["frames"]
    
    # Get all fields (no exclusion)
    cursor = collection.find({}).sort("created_at", -1).limit(limit)
    
    results = []
    for doc in cursor:
        # 1. Convert ObjectId to string
        doc["_id"] = str(doc["_id"]) 
        
        # 2. Convert 'created_at' to string (if it's a datetime object)
        if "created_at" in doc:
            doc["created_at"] = str(doc["created_at"])

        # 3. CRITICAL FIX: Convert Image Bytes to Base64 String
        if "image_data" in doc:
            image_data = doc["image_data"]
            
            # If stored as BSON Binary or raw bytes, convert to base64 string
            if isinstance(image_data, (bytes, Binary)):
                # Encode bytes to base64 bytes, then decode to utf-8 string
                encoded_str = base64.b64encode(image_data).decode('utf-8')
                doc["image_data"] = encoded_str
        
        results.append(doc)
        
    return results