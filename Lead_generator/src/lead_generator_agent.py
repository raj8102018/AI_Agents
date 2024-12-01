"""This module handles the functionality of the lead generator agent."""
# pylint: disable=import-error
# pylint: disable=wrong-import-position
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Database.lead_generator_connector import update_leads, connect_to_mongodb, fetch_leads, fetch_leads_for_user, fetch_agent_and_company_name

from .lead_classification import lead_classification_update
from .response_generation import batch_processing, get_batches

class LeadGenerator:
    """
    This class contains methods for lead generator agent
    """
    def __init__(self):
        pass

    def run(self):
        """Indicates the start of the agent."""
        print("Running Lead Generation Agent...")
        database = connect_to_mongodb()
        leads_collection = database["leads"]
        return leads_collection

    def fetch_and_classify(self,leads_collection, user_id):
        """To fetch the leads and run classification."""
        print("Fetching lead data....")
        leads_list = fetch_leads_for_user(leads_collection, user_id)
        print("Classifying...")
        leads = lead_classification_update(leads_list)
        return leads
    
    def process_and_update(self, info, user_id):
        """Contains the method that makes api calls and fetches custom responses"""
        print("processing lead data and crafting custom messages...")
        batches = get_batches(info)
        print("get batches info working")
        print(f"batches:{batches}")
        user_details = fetch_agent_and_company_name(user_id)
        company_name = user_details["company_name"]
        agent_name = user_details["agent_name"]
        batches = batch_processing(batches,agent_name,company_name)
        merged_list = [item for sublist in batches for item in sublist]
        print(f"merged list : {merged_list}")
        print("updating the database with custom responses")
        update_leads(merged_list)
        print("Successfully updated")
