from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from config.settings import MONGODB_URI, MONGODB_DB

def connect_to_mongodb():
    # Use the MongoDB URI from the settings
    client = MongoClient(MONGODB_URI)
    
    # Access the specific database
    db = client[MONGODB_DB]
    
    # Access the 'users' collection
    leads_collection = db['users']
    
    # Return the collection for further use
    return leads_collection


def get_user_by_email(email,leads_collection):
    return leads_collection.find_one({"email": email})

def get_user_by_username(username,leads_collection):
    return leads_collection.find_one({"username": username})

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

# User creation function
def create_user(first_name,last_name,user_name,email, password):
    leads_collection = connect_to_mongodb()
    if get_user_by_email(email,leads_collection):
        return False  # User already exists
    if get_user_by_username(user_name,leads_collection):
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
    

 


