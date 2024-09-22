import os
import sys
import time
import random
from pymongo import MongoClient
from bson.objectid import ObjectId

from transformers import BertTokenizer, TFBertForSequenceClassification, AdamWeightDecay

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import MONGODB_URI, MONGODB_DB
from src.response_generation import batch_processing, get_batches
from src.lead_classification import lead_classification_update
from src.mongodb_integration import update_leads

# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    leads_collection = db['leads']
    return leads_collection

#Creating random leads based on list of industries and job titles available
Industries  = ['IT Services And IT Consulting', 'Software Development', 
            'Medical Device', 'Pharmaceuticals', 'Business Consulting And Services',
            'Hospitals And Health Care','Health, Wellness & Fitness', 'Nonprofit Organizations', 
            'Government Administration', 'Manufacturing', 
            'Appliances, Electrical, And Electronics Manufacturing','Retail',  'Environmental Services', 'Design Services', 
            'Wholesale']
Job_titles  = ['Chief Executive Officer', 'President', 'Founder', 
            'Vice President', 'Director','Executive Director', 'Managing Director', 'Owner', 
            'General Manager', 'Vice President of Operations','CoOwner', 'Deputy Director', 'Executive Vice President']
count = 20 #limiting the test size to 20
new_lead_list = []
for i in range(count):
    ind_index = random.randint(0,len(Industries)-1)
    job_index = random.randint(0,len(Job_titles)-1)
    new_lead = {
        'Company': f'test#{i+1}',
        'Website': f'test#{i+1}',
        'Industry': Industries[ind_index],
        'Address Street': f'test#{i+1}',
        'City': f'test#{i+1}',
        'State': f'test#{i+1}',
        'Zip Code': f'test#{i+1}',
        'Country': f'test#{i+1}',
        'Contact Number': f'test#{i+1}',
        'First Name': f'test#{i+1}',
        'Last Name': f'test#{i+1}',
        'Job Title': Job_titles[job_index],
        'Email': f'test#{i+1}@example.com',
        'Linkedin URL': f'test#{i+1}'
        }
    new_lead_list.append(new_lead)

# Function to add a new lead to the database
def add_new_leads(leads_list):
    leads_collection = connect_to_mongodb()
    
    # Insert the list of new leads into the 'leads' collection
    result = leads_collection.insert_many(leads_list)
    
    # Print the IDs of the inserted documents
    return result.inserted_ids

# Function to delete multiple leads based on a list of lead IDs
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

# flow of the text exectution
print(f"The lead list is as follows : {new_lead_list}\n")
print('\n')
print("adding the leads to the database!!!\n")
add_new_leads(new_lead_list)
print("new leads added!!\n")
print("fetching the leads from the database for classification\n")
lead_info = lead_classification_update()
print("segregating the classified leads into batches\n")
batches = get_batches(lead_info)
print("testing the response_generation by passing the leads to the api \n")
processed_batches = batch_processing(batches)
print("updating the batches to the database\n")
update_leads(processed_batches)
print("giving the user time to check for the update in the database\n")
time.sleep(60)
print("deleting the dummy leads from the database\n")
delete_leads(processed_batches)
print("leads have been deleted from the database\n")
print("the agent is working as expected!!!")