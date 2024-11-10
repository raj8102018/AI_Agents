"""This module handles the functionality of the agent."""
# pylint: disable=import-error
# pylint: disable=wrong-import-position
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Database.lead_generator_connector import update_leads, connect_to_mongodb, fetch_leads

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
        return connect_to_mongodb()

    def fetch_and_classify(self,leads_collection):
        """To fetch the leads and run classification."""
        print("Fetching lead data....")
        leads_list = fetch_leads(leads_collection)
        print("Classifying...")
        leads = lead_classification_update(leads_list)
        return leads

    def process_and_update(self, info):
        """Contains the method that makes api calls and fetches custom responses"""
        print("processing lead data and crafting custom messages...")
        batches = get_batches(info)
        batches = batch_processing(batches)
        merged_list = [item for sublist in batches for item in sublist]
        print("updating the database with custom responses")
        update_leads(merged_list)
        print("Successfully updated")
