from pymongo import MongoClient

# Singleton client to reuse connection
client = None

def get_mongo_db():
    global client
    if client is None:
        # Connect to local MongoDB
        client = MongoClient("mongodb://localhost:27017/")
    
    # Return the specific database
    return client["yolo"] # This matches the DB name you saw in mongosh