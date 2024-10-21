from flask import Flask, jsonify, request, g  # g is used to store global data for the request
from flask_cors import CORS  # For enabling CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from config.settings import MONGODB_URI, MONGODB_DB

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize MongoDB connection at app startup
def get_mongo_client():
    if 'mongo_client' not in g:  # If not already connected, create a client
        g.mongo_client = MongoClient(MONGODB_URI)
    return g.mongo_client

# Access MongoDB collection
def get_mongo_collection():
    client = get_mongo_client()
    db = client[MONGODB_DB]
    return db['users']

@app.teardown_appcontext
def close_mongo_client(exception=None):
    """Close the MongoDB client when the app context is torn down."""
    mongo_client = g.pop('mongo_client', None)
    if mongo_client is not None:
        mongo_client.close()

# Helper Functions
def get_user_by_email(email):
    leads_collection = get_mongo_collection()
    return leads_collection.find_one({"email": email})

def get_user_by_username(username):
    leads_collection = get_mongo_collection()
    return leads_collection.find_one({"username": username})

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

def create_user(first_name, last_name, user_name, email, password):
    leads_collection = get_mongo_collection()
    if get_user_by_email(email):
        return False  # User already exists
    if get_user_by_username(user_name):
        return False

    hash_password = generate_password_hash(password)
    user = {
        "email": email,
        "password": hash_password,
        "username": user_name,
        "firstname": first_name,
        "lastname": last_name,
    }
    leads_collection.insert_one(user)
    return True
