"""
This module contains the functionality for database and authentication code
"""
import os
import sys
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, g # g is used to store global data for the request #pylint: disable=unused-import
from flask_cors import CORS  # For enabling CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# Add the parent directory to the Python path to access 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Config.settings import MONGODB_URI, MONGODB_DB_AUTH #pylint: disable=wrong-import-position


# Initialize Flask app
app = Flask(__name__)
CORS(app)


def get_mongo_client():
    """Function to initialize MongoDB connection at app startup"""
    if "mongo_client" not in g:  # If not already connected, create a client
        g.mongo_client = MongoClient(MONGODB_URI)
    return g.mongo_client


def get_mongo_collection():
    """Function to access mongodb collection"""
    client = get_mongo_client()
    db = client[MONGODB_DB_AUTH]
    return db["users"]


@app.teardown_appcontext
def close_mongo_client(exception=None):
    """Close the MongoDB client when the app context is torn down."""
    mongo_client = g.pop("mongo_client", None)
    if mongo_client is not None:
        mongo_client.close()


def get_user_by_email(email):
    """helper function to get user by email"""
    leads_collection = get_mongo_collection()
    return leads_collection.find_one({"email": email})


def get_user_by_username(username):
    """helper function to get user by username"""
    leads_collection = get_mongo_collection()
    return leads_collection.find_one({"username": username})

def get_user_by_id(id):
    """helper function to get user by username"""
    leads_collection = get_mongo_collection()
    user = leads_collection.find_one({"_id": ObjectId(id)})
    user["_id"] = str(user["_id"])
    return user

def verify_password(stored_password, provided_password):
    """helper function to verify password"""
    return check_password_hash(stored_password, provided_password)


def create_user(first_name, last_name, user_name, email, password):
    """function to create user"""
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


def create_guser(name, email):
    """"function to add user authenticated via google"""
    leads_collection = get_mongo_collection()
    user = get_user_by_email(email)
    if user:
        return user  # User already exists
    user = {
        "email": email,
        "name": name,
        "oauth_provider": "google",  # Optional field to store OAuth provider
    }
    leads_collection.insert_one(user)
    user = get_user_by_email(email)
    return user
