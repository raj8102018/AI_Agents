"""
This module is to make API calls, fetch responses, and conduct batch processing.
"""
import sys     
import dspy
import os
import openai
import time
from dotenv import load_dotenv
load_dotenv()

from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException # pylint: disable=redefined-builtin
# from .lead_generator_prompts import outbound_prompt

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "src")))


def get_batches(data, batch_size=10):
    """This function batches the given data to avoid hitting api input limits"""
    batches = []
    list_length = len(data)

    if list_length == 0:
        return []  # or another appropriate response

    for i in range(0, list_length, batch_size):
        batches.append(data[i : i + batch_size])  # Slice directly

    return batches

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
lm = dspy.LM('openai/gpt-4o-mini', api_key=api_key)
dspy.configure(lm=lm)

def format_prompt(leads, executive_name, company_name):
    batch_len = len(leads)
    formatted_leads = f"You are given a batch of {batch_len} leads as follows:\n"
    
    for idx, lead in enumerate(leads):
        formatted_leads += (
            f"Lead {idx + 1}:\n"
            f"Company: {lead['Company']}\n"
            f"Executive: {lead['First Name']} {lead['Last Name']}\n"
            f"Job Title: {lead['Job Title']}\n"
            f"Industry: {lead['Industry']}\n\n"
        )

    outbound_message_template = f"""
    For each lead, generate a **complete outbound email** in a professional format. Each email must include:
    - A **subject line** specific to the lead's company and industry.
    - A personalized **greeting** using the lead's name.
    - A detailed **message body** introducing yourself as {executive_name} from {company_name}. Mention your company's focus on AI integration solutions to streamline business processes and highlight how these solutions can provide value to the lead's company, role, and industry.
    - A polite **closing** and your professional **email signature**.

    Respond with the emails directly, with no placeholders or additional instructions.
    """
    return formatted_leads + outbound_message_template


class OutboundEmailSignature(dspy.Signature):
    """Generate complete outbound emails for leads."""
    
    leads: list[dict] = dspy.InputField(desc="List of lead dictionaries containing details such as Company, Executive, Job Title, and Industry.")
    executive_name: str = dspy.InputField(desc="Your name as the sales executive.")
    company_name: str = dspy.InputField(desc="Your company's name.")
    emails: list[str] = dspy.OutputField(desc="Generated emails with subject, body, and signature without designation.")


generate_emails = dspy.ChainOfThought(OutboundEmailSignature)

def batch_processing(batches_to_process,executive_name, company_name):
    """This function processes the batches in time intervals"""
    print("batch_processing started")
    for batch in batches_to_process:
        print("going into generate_response")
        print(batch)
        print('\n')
        batch_response = generate_emails(leads=batch, executive_name=executive_name, company_name=company_name).emails
        for i in range(0, len(batch)):
            batch[i]["outbound message"]= batch_response[i]
        time.sleep(10)
    return batches_to_process


if __name__ == "__main__":
    
    batches = [[
        {'Company': 'Sonic Solutions', 'First Name': 'Rajendra', 'Last Name': 'P', 'Job Title': 'Director', 'Industry': 'Motor Racing'},
        {'Company': 'hedgehog Solutions', 'First Name': 'Prasad', 'Last Name': 'K', 'Job Title': 'Chief Executive Officer', 'Industry': 'Pullaice'}
    ]]

    executive_name = "Alice Johnson"
    company_name = "Acme Corp"

    response_list = batch_processing(batches, executive_name, company_name)
    print('\n\n\n\n') 
    print(response_list)
    