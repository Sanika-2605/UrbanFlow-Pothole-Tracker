from pymongo import MongoClient

# Connect to your local MongoDB server
client = MongoClient("mongodb://localhost:27017/")

# Create or connect to database
db = client["pothole_db"]

# Create or use the collection for pothole reports
pothole_collection = db["pothole_reports"]
