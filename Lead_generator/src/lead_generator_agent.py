"""This module handles the functionality of the agent."""
import os
import sys
from lead_classification import lead_classification_update # pylint: disable=import-error
from response_generation import batch_processing, get_batches # pylint: disable=import-error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from Database.lead_generator_connector import update_leads


class LeadGenerator:
    """
    This class contains methods for lead generator agent
    """
    def __init__(self):
        pass

    def run(self):
        """Indicates the start of the agent."""
        print("Running Lead Generation Agent...")

    def classify_and_update(self):
        """To fetch the leads and run classification."""
        print("Fetching lead data and classifying...")
        return lead_classification_update()

    def process_and_update(self, info):
        """Contains the method that makes api calls and fetches custom responses"""
        print("processing lead data and crafting custom messages...")
        batches = get_batches(info)
        batches = batch_processing(batches)
        merged_list = [item for sublist in batches for item in sublist]
        print("updating the database with custom responses")
        update_leads(merged_list)
        print("Successfully updated")

if __name__ == "__main__":
    my_obj = LeadGenerator()
    my_obj.run()
    lead_info = my_obj.classify_and_update()
    my_obj.process_and_update(lead_info)
