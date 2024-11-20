"""
This module contains the functionality for the orchestrator
"""

import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Lead_generator"))
)

# orchestrator/orchestrator.py
from lead_generator.src.lead_generator_agent import LeadGenerator
from email_automation.src.email_automation_agent import EmailAutomation


class Orchestrator:
    """This class contains all the methods for orchestrator functionality"""

    def __init__(self):
        # Set up database connection
        # Initialize and register agents
        self.agents = {
            "lead_classification": LeadGenerator,
            "email_automation": EmailAutomation,
        }

    def run(self):
        """This method contains the sequential flow of agent logic"""
        # Order of execution
        print("Starting Orchestrator...")

        # Step 1: Run Lead Classification Agent
        leads_collection = self.agents["lead_classification"].run(self)

        leads = self.agents["lead_classification"].fetch_and_classify(
            self, leads_collection
        )

        self.agents["lead_classification"].process_and_update(self, leads)

        # Step 2: Run Email Automation Agent
        self.agents["email_automation"].run(self)

        self.agents["email_automation"].initiate_email(self)

        self.agents["email_automation"].bulk_reply(self)

        print("Orchestrator finished execution.")


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
