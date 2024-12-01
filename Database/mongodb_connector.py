"Functionality related to database integration for email automation and meet buddy agents"
# In mongodb_integration.py
import sys
import os
import re
import json
from pymongo import MongoClient
from pymongo import UpdateOne
from bson.objectid import ObjectId


# Add the parent directory to the Python path to access 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Config.settings import MONGODB_URI, MONGODB_DB #pylint: disable=wrong-import-position

def connect_to_mongodb():
    """This function makes the connection to mongodb"""
    # Use the MongoDB URI from the settings
    client = MongoClient(MONGODB_URI)

    # Access the specific database
    db = client[MONGODB_DB]

    # Access the 'leads' collection
    leads_collection = db['leads']
    # leads_collection = db['test_emails']


    return leads_collection
    # return "connect successful"

def get_sender_email(user_id):
    client = MongoClient(MONGODB_URI)

    # Access the specific database
    db = client[MONGODB_DB]

    # Access the 'leads' collection
    users_collection = db['users']
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    return user["email"]

def get_user_gmail_token(user_id):
    client = MongoClient(MONGODB_URI)

    # Access the specific database
    db = client[MONGODB_DB]

    # Access the 'leads' collection
    users_collection = db['users']
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    return json.loads(user.get("gtoken")) 

def fetch_leads(user_id, leads_collection):
    """This function fetches the leads"""
    # try:
    # Fetch documents where 'initial_contact' is 'No'
    leads = leads_collection.find({
        "user_id": ObjectId(user_id),
        "Initial contact": {"$in": ["No", "no"]},
    })
    leads_list = list(leads)  # Caution: consider cursor iteration if too many leads
    return leads_list
    # except Exception as e: #pylint: disable=broad-exception-caught
    #     print(f"Error fetching leads: {e}")
    #     return []

def leads_for_initial_contact(user_id, leads_collection):
    """this function filters the leads that are yet to be contacted"""
    leads_list = fetch_leads(user_id, leads_collection)
    subject_regex = r"(?<=[sS]ubject:\s)(.*?)(?=\n\n)"
    # messagebody_regex = r"(?<=\n\n)(.*)"
    mail_batch_initial = []
    for entry in leads_list:
        lead_details = {}
        lead_details['recepient'] = entry['Email']
        subject_str = re.search(subject_regex, entry['outbound message'])
        if subject_str:
            subject_str = subject_str.group()
        lead_details['subject'] = subject_str
        # lead_details['content'] = re.search(messagebody_regex, entry['outbound message']).group()
        lead_details['content'] = re.split(subject_regex, entry['outbound message'])[-1]
        mail_batch_initial.append(lead_details)
    return mail_batch_initial,leads_list


def update_leads(batch,leads_collection):
    """This functioon updates the leads back"""

    # Create a list to hold update operations
    operations = []

    # Prepare the update operations for each lead
    for lead in batch:
        operation = UpdateOne(
            {'_id': lead['_id']},  # Filter to match the lead's unique ID
            {'$set': {
                  # Set the lead_type field
                'Initial contact': 'Yes'  # Set the outbound message field
            }}
        )
        operations.append(operation)  # Add the operation to the list

    # Perform the bulk write operation
    if operations:  # Check if there are operations to execute
        result = leads_collection.bulk_write(operations)
    else:
        result = None
    return result  # Return the result of the bulk write operation

if __name__ == "__main__":
    print(leads_for_initial_contact(connect_to_mongodb()))