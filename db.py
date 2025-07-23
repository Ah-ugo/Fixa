from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import Union

load_dotenv()

# Load MongoDB URI from environment variable
MONGO_URI = os.getenv("MONGO_URL")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["service_app"]


class RoleFilteredCollection:
    def __init__(self, collection, role: Union[str, None] = None):
        self.collection = collection
        self.role = role

    def find(self, *args, **kwargs):
        if self.role:
            if 'filter' in kwargs:
                kwargs['filter']['role'] = self.role
            elif args and isinstance(args[0], dict):
                args[0]['role'] = self.role
            else:
                kwargs['filter'] = {'role': self.role}
        return self.collection.find(*args, **kwargs)

    def find_one(self, *args, **kwargs):
        if self.role:
            if 'filter' in kwargs:
                kwargs['filter']['role'] = self.role
            elif args and isinstance(args[0], dict):
                args[0]['role'] = self.role
            else:
                kwargs['filter'] = {'role': self.role}
        return self.collection.find_one(*args, **kwargs)

    def __getattr__(self, name):
        # Pass through all other methods to the original collection
        return getattr(self.collection, name)

# Collections
users_collection = db["users"]
providers_collection = RoleFilteredCollection(db["users"], role="provider")
admins_collection = RoleFilteredCollection(db["users"], role="admin")
regular_users_collection = RoleFilteredCollection(db["users"], role="user")
services_collection = db["services"]
bookings_collection = db["bookings"]
wallets_collection = db["wallets"]
transactions_collection = db["transactions"]
reviews_collection = db["reviews"]
support_tickets_collection = db["support_tickets"]
# admins_collection = db["admins"]
notifications_collection = db["notifications"]
messages_collection = db["messages"]

# Function to get database
def get_db():
    return db
