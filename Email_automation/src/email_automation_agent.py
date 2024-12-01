"""This module contains the functionality of the agent packaged in a class """

from .gmail_integration import (
    authenticate_gmail_api,
    batch_mail_initiation,
    batch_reply,
)  # pylint: disable=import-error


class EmailAutomation:
    """This class contains the methods for all functions performed by the agent"""

    def __init__(self):
        pass

    def run(self, user_id):
        """This function starts the agent"""
        authenticate_gmail_api(user_id)
        print("Running Email Automation Agent...")

    def initiate_email(self, user_id):
        """This method calls the function that initiates the conversation"""
        print("Sending initial emails")
        print(user_id)
        batch_mail_initiation(user_id)

    def bulk_reply(self, user_id, company_name):
        """this methods calls the function that sends a batch of replies"""
        print("segregating mails and responding")
        batch_reply(user_id, company_name)
