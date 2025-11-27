import base64
import json
from datetime import datetime
from db.mongo_connection import get_mongo_db

# from database import get_mongo_db  <-- Verify your import path

def insert_depth_result(data):
    """
    Saves the analyzed depth frame and object data to MongoDB.
    :param data: The dictionary containing 'image' (base64) and 'objects' (list)
    """
    db = get_mongo_db()
    collection = db["depth"]  # Storing data in the 'depth' collection

    # 1. Extract and Decode Base64 Image
    base64_string = data.get("image", "")
    
    # Remove header if present (e.g., "data:image/jpeg;base64,...")
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    try:
        image_binary = base64.b64decode(base64_string)
    except Exception as e:
        print(f"Error decoding base64: {e}")
        image_binary = None

    # 2. Get Object Data
    objects = data.get("objects", [])

    # 3. Create the document structure
    document = {
        "created_at": datetime.utcnow(),
        "image_data": image_binary,      # Storing as Binary (more efficient than B64 string)
        "object_count": len(objects),
        "objects": objects               # List of objects with distances
    }

    # 4. Insert into MongoDB
    result = collection.insert_one(document)
    
    return str(result.inserted_id)