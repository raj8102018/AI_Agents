# orchestrator/orchestrator.py
from Email_automation.src.email_automation_agent import EmailAutomationAgent
from Email_automation.src.mongodb_integration import EmailAutomationAgent

class Orchestrator:
    def __init__(self):
        # Set up database connection
        self.db_connector = MongoDBConnector()
        
        # Initialize and register agents
        self.agents = {
            "lead_classification": LeadClassificationAgent(self.db_connector),
            "email_automation": EmailAutomationAgent(self.db_connector)
        }
    
    def run(self):
        # Order of execution
        print("Starting Orchestrator...")
        
        # Step 1: Run Lead Classification Agent
        self.agents["lead_classification"].run()
        
        # Step 2: Run Email Automation Agent
        self.agents["email_automation"].run()
        
        print("Orchestrator finished execution.")
