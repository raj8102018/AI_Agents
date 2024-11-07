# In mongodb_integration.py
from pymongo import MongoClient
from pymongo import UpdateOne
import sys
import os
import re
from bson.objectid import ObjectId


# Add the root directory to the Python path to access 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import MONGODB_URI, MONGODB_DB

def connect_to_mongodb():
    # Use the MongoDB URI from the settings
    client = MongoClient(MONGODB_URI)
    
    # Access the specific database
    db = client[MONGODB_DB]
    
    # Access the 'leads' collection
    leads_collection = db['test_emails']
    
    return leads_collection
    #return "connect successful"

def fetch_leads():
    try:
        leads_collection = connect_to_mongodb()
        # Fetch documents where 'initial_contact' is 'No'
        leads = leads_collection.find({
            'Initial contact': {'$eq': 'No'},
        })
        leads_list = list(leads)  # Caution: consider cursor iteration if too many leads
        return leads_list
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []

def leads_for_initial_contact():
    leads_list = fetch_leads()
    subject_regex = r"(?<=Subject:\s)(.*?)(?=\\n\\n)"
    messagebody_regex = r"(?<=\\n\\n)(.*)"
    mail_batch_initial = []
    for entry in leads_list:
        lead_details = {}
        lead_details['recepient'] = entry['Email']
        lead_details['subject'] = re.search(subject_regex, entry['outbound message']).group()
        lead_details['content'] = re.search(messagebody_regex, entry['outbound message']).group()
        mail_batch_initial.append(lead_details)
    return mail_batch_initial

def update_leads(batch):
    leads_collection = connect_to_mongodb()

    # Create a list to hold update operations
    operations = [] 

    # Prepare the update operations for each lead
    for lead in batch:
        operation = UpdateOne(
            {'_id': lead['_id']},  # Filter to match the lead's unique ID
            {'$set': {
                'lead_type': lead['lead_type'],  # Set the lead_type field
                'outbound message': lead['outbound message']  # Set the outbound message field
            }}
        )
        operations.append(operation)  # Add the operation to the list

    # Perform the bulk write operation
    if operations:  # Check if there are operations to execute
        result = leads_collection.bulk_write(operations)

    return result  # Return the result of the bulk write operation



# Function to add a new lead to the database
def add_new_leads(leads_list):
    leads_collection = connect_to_mongodb()
    
    # Insert the list of new leads into the 'leads' collection
    result = leads_collection.insert_many(leads_list)
    
    # Print the IDs of the inserted documents
    return result.inserted_ids

def delete_leads(lead_id_list):
    leads_collection = connect_to_mongodb()
    
    # Convert all lead IDs to ObjectId format
    object_id_list = [ObjectId(lead_id) for lead_id in lead_id_list]
    
    # Delete the leads with the specified IDs using $in operator
    result = leads_collection.delete_many({'_id': {'$in': object_id_list}})
    
    # Check how many documents were deleted
    if result.deleted_count > 0:
        print(f"{result.deleted_count} leads have been deleted.")
    else:
        print("No leads found with the specified IDs.")

if __name__ == "__main__":
    
    # output = leads_for_initial_contact()
    # for i in output:
    #     print(i,'\n')
    print(fetch_leads())
