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

def get_latest_depth_result():
    """
    Retrieves the most recently added document from the 'depth' collection.
    Converts binary image data back to a Base64 string for JSON serialization.
    """
    db = get_mongo_db()
    collection = db["depth"]

    # 1. Find the latest document
    # Sort by 'created_at' in descending order (-1) to get the newest first
    latest_doc = collection.find_one(sort=[("created_at", -1)])

    if not latest_doc:
        return None

    # 2. Process the document for output
    
    # Convert ObjectId to string (JSON serializable)
    latest_doc["_id"] = str(latest_doc["_id"])

    # Convert Binary image data back to Base64 string
    if "image_data" in latest_doc and latest_doc["image_data"]:
        try:
            # Encode binary -> base64 bytes -> utf-8 string
            b64_bytes = base64.b64encode(latest_doc["image_data"])
            latest_doc["image"] = b64_bytes.decode('utf-8')
            
            # Optional: Remove the raw binary field to make the dict JSON serializable
            del latest_doc["image_data"]
        except Exception as e:
            print(f"Error encoding image to base64: {e}")
            latest_doc["image"] = None

    return latest_doc