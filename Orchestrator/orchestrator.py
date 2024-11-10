"""
This module contains the functionality for the orchestrator
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Lead_generator')))

# orchestrator/orchestrator.py
from Lead_generator.src.lead_generator_agent import LeadGenerator
from Email_automation.src.email_automation_agent import EmailAutomation

class Orchestrator:
    """This class contains all the methods for orchestrator functionality"""
    def __init__(self):
        # Set up database connection
        # self.run = LeadGenerator
        
        # Initialize and register agents
        self.agents = {
            "lead_classification": LeadGenerator,
            "email_automation": EmailAutomation
        }
    
    def run(self):
        # Order of execution
        print("Starting Orchestrator...")
        
        # Step 1: Run Lead Classification Agent
        self.agents["lead_classification"].run(self)
        
        # Step 2: Run Email Automation Agent
        self.agents["email_automation"].run(self)
        
        print("Orchestrator finished execution.")
        
if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
