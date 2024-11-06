from mongodb_integration import connect_to_mongodb, fetch_leads, update_leads, add_new_leads, delete_leads
from model import predict_lead
from lead_classification import classify_lead, lead_classification_update
from response_generation import batch_processing, get_batches

class Lead_generator:
    def __init__(self):
        pass
    
    def run(self):
        print("Running Lead Generation Agent...")
        
    def classify_and_update(self):
        print(f"Fetching lead data and classifying...")
        return lead_classification_update()
    
    def process_and_update(self, lead_info):
        print(f"processing lead data and crafting custom messages...")
        batches = get_batches(lead_info)
        batches = batch_processing(batches) 
        merged_list = [item for sublist in batches for item in sublist]
        print(f"updating the database with custom responses")
        update_leads(merged_list)
        print("Successfully updated")    
        
if __name__ == "__main__":
    my_obj = Lead_generator()
    my_obj.run()
    lead_info = my_obj.classify_and_update()
    my_obj.process_and_update(lead_info)