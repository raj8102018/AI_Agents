import os
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import MONGODB_URI, MONGODB_DB

# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    leads_collection = db['leads']
    return leads_collection

# Function to add a new lead to the database
def add_new_lead(new_lead):
    leads_collection = connect_to_mongodb()
    
    # Insert the new lead into the 'leads' collection
    result = leads_collection.insert_one(new_lead)
    
    # Print the ID of the inserted document
    print(f"New lead added with ID: {result.inserted_id}")

# Example new lead document to add
new_lead = {
    'Company': 'New Company',
    'Website': 'newcompany.com',
    'Industry': 'Technology',
    'Address Street': '123 New Street',
    'City': 'New York',
    'State': 'New York',
    'Zip Code': 10001,
    'Country': 'United States',
    'Contact Number': '1 212 555 1234',
    'First Name': 'John',
    'Last Name': 'Doe',
    'Job Title': 'CTO',
    'Email': 'john.doe@newcompany.com',
    'Linkedin URL': 'https://linkedin.com/in/johndoe'
}

# Call the function to add the new lead
add_new_lead(new_lead)


# Function to delete a lead from the database
def delete_lead(lead_id):
    leads_collection = connect_to_mongodb()
    
    # Delete the lead with the specified ID
    result = leads_collection.delete_one({'_id': ObjectId(lead_id)})
    
    # Check if a document was deleted
    if result.deleted_count > 0:
        print(f"Lead with ID {lead_id} has been deleted.")
    else:
        print(f"No lead found with ID {lead_id}.")

# Example lead ID to delete
lead_id_to_delete = '66ebcdb633778cd97ba4c365'  # Replace with the actual ID of the lead to delete

# Call the function to delete the lead
delete_lead(lead_id_to_delete)
