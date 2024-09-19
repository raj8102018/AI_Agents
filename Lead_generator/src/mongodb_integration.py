# In mongodb_integration.py
from pymongo import MongoClient

def connect_to_mongodb():
    client = MongoClient("mongodb+srv://21ev06003:5vKMpYJAtIkyCxj8@cluster0.ell23.mongodb.net/")
    db = client['lead_generation_db']
    leads_collection = db['leads']
    return leads_collection

def fetch_leads():
    leads_collection = connect_to_mongodb()
    leads = leads_collection.find({})
    return leads

