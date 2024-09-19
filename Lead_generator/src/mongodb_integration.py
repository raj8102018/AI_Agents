# In mongodb_integration.py
from pymongo import MongoClient
import sys
import os

# Add the root directory to the Python path to access 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import MONGODB_URI, MONGODB_DB

def connect_to_mongodb():
    # Use the MongoDB URI from the settings
    client = MongoClient(MONGODB_URI)
    
    # Access the specific database
    db = client[MONGODB_DB]
    
    # Access the 'leads' collection
    leads_collection = db['leads']
    
    return leads_collection

def fetch_leads():
    leads_collection = connect_to_mongodb()
    leads = leads_collection.find({})
    leads_list = list(leads)
    return leads_list

# Example usage
if __name__ == "__main__":
    leads = fetch_leads()
    for lead in leads:
        print(lead)
