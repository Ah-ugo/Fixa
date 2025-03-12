from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Load MongoDB URI from environment variable
MONGO_URI = os.getenv("MONGO_URL")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["service_app"]

# Collections
users_collection = db["users"]
providers_collection = db["providers"]
services_collection = db["services"]
bookings_collection = db["bookings"]
wallets_collection = db["wallets"]
transactions_collection = db["transactions"]
reviews_collection = db["reviews"]
support_tickets_collection = db["support_tickets"]
admins_collection = db["admins"]
notifications_collection = db["notifications"]
messages_collection = db["messages"]

# Function to get database
def get_db():
    return db
