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
    leads = leads_collection.find({
        'lead_type': {'$exists': False},   # Documents without 'lead_type'
        'outbound message': {'$exists': False}  # Documents without 'outbound message'
    })
    leads_list = list(leads)
    return leads_list

# Update leads in the MongoDB collection with 'lead_type' and 'outbound message'
def update_leads(lead):
    leads_collection = connect_to_mongodb()
        # Update the document in the database with the new key-value pairs
    leads_collection.update_one(
        {'_id': lead['_id']},  # Match by the lead's unique ID
        {'$set': {'lead_type': lead['lead_type'], 'outbound message': lead['outbound message']}}
    )
    #print(f"Updated lead: {lead['_id']} with lead_type: {lead['lead_type']} and outbound message: {lead['outbound message']}")



# # Example usage
# if __name__ == "__main__":
#     leads = fetch_leads()
#     for lead in leads:
#         print(lead)
