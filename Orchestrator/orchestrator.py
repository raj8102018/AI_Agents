"""
This module contains the functionality for the orchestrator
"""

import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Lead_generator"))
)

# orchestrator/orchestrator.py
from Lead_generator.src.lead_generator_agent import LeadGenerator
from Email_automation.src.email_automation_agent import EmailAutomation


class Orchestrator:
    """This class contains all the methods for orchestrator functionality"""

    def __init__(self, user_id,company_name):
        # Set up database connection
        # Initialize and register agents
        self.agents = {
            "lead_classification": LeadGenerator,
            "email_automation": EmailAutomation
        }
        self.user_id = user_id
        self.company_name = company_name

    def run(self):
        """This method contains the sequential flow of agent logic"""
        # Order of execution
        print("Starting Orchestrator...")

        # Step 1: Run Lead Classification Agent
        leads_collection = self.agents["lead_classification"].run(self)

        leads = self.agents["lead_classification"].fetch_and_classify(
            self, leads_collection, self.user_id
        )

        self.agents["lead_classification"].process_and_update(self, leads)

        # Step 2: Run Email Automation Agent
        self.agents["email_automation"].run(self, self.user_id)
        print(self.company_name)
        print(self.user_id)
        self.agents["email_automation"].initiate_email(self, self.user_id)

        self.agents["email_automation"].bulk_reply(self, self.user_id,self.company_name)

        print("Orchestrator finished execution.")


if __name__ == "__main__":
    orchestrator = Orchestrator("67456a9246b3ff5be3ccc541","QState")
    orchestrator.run()
