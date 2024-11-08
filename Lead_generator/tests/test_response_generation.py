"""
This module consists of basic testing of functions written in src module
"""
#pylint: disable=import-error
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import sys
import random
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Lead_generator.src.response_generation import batch_processing, get_batches #pylint: disable=wrong-import-position
from Lead_generator.src.lead_classification import lead_classification_update #pylint: disable=wrong-import-position
from Database.lead_generator_connector import update_leads,connect_to_mongodb, add_new_leads, delete_leads #pylint: disable=wrong-import-position

# Creating random leads based on list of industries and job titles available
Industries = [
    "IT Services And IT Consulting",
    "Software Development",
    "Medical Device",
    "Pharmaceuticals",
    "Business Consulting And Services",
    "Hospitals And Health Care",
    "Health, Wellness & Fitness",
    "Nonprofit Organizations",
    "Government Administration",
    "Manufacturing",
    "Appliances, Electrical, And Electronics Manufacturing",
    "Retail",
    "Environmental Services",
    "Design Services",
    "Wholesale",
]
Job_titles = [
    "Chief Executive Officer",
    "President",
    "Founder",
    "Vice President",
    "Director",
    "Executive Director",
    "Managing Director",
    "Owner",
    "General Manager",
    "Vice President of Operations",
    "CoOwner",
    "Deputy Director",
    "Executive Vice President",
]

COUNT = 5  # limiting the test size to 20
new_lead_list = []
for i in range(COUNT):
    ind_index = random.randint(0, len(Industries) - 1)
    job_index = random.randint(0, len(Job_titles) - 1)
    new_lead = {
        "Company": f"test#{i+1}",
        "Website": f"test#{i+1}",
        "Industry": Industries[ind_index],
        "Address Street": f"test#{i+1}",
        "City": f"test#{i+1}",
        "State": f"test#{i+1}",
        "Zip Code": f"test#{i+1}",
        "Country": f"test#{i+1}",
        "Contact Number": f"test#{i+1}",
        "First Name": f"test#{i+1}",
        "Last Name": f"test#{i+1}",
        "Job Title": Job_titles[job_index],
        "Email": f"test#{i+1}@example.com",
        "Linkedin URL": f"test#{i+1}",
    }
    new_lead_list.append(new_lead)


#flow of the text exectution
connect_to_mongodb()
print(f"The lead list is as follows : {new_lead_list}\n")
print("\n")
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
merged_list = [item for sublist in processed_batches for item in sublist]
# Update the leads to the database
update_leads(merged_list)
print(merged_list)
object_id_list = [entry['_id'] for entry in merged_list]
print(object_id_list)
print("giving the user time to check for the update in the database\n")
time.sleep(30)
print("deleting the dummy leads from the database\n")
delete_leads(object_id_list)
print("leads have been deleted from the database\n")
print("the agent is working as expected!!!")
