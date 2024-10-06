import sys
import os
import time
import logging
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

import tensorflow as tf

# Suppress most messages:
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

from mongodb_integration import update_leads

from dotenv import load_dotenv
import google.generativeai as genai
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from lead_classification import lead_classification_update

lead_info = lead_classification_update()

def get_batches(data, batch_size=10):
	batches = []
	list_length = len(data)

	if list_length == 0:
		return []  # or another appropriate response

	for i in range(0, list_length, batch_size):
		batches.append(data[i:i + batch_size])  # Slice directly

	return batches

# from config.settings import GOOGLE_API_KEY

# Load environment variables from .env file
load_dotenv()

def generate_response(batch):
	# Format the batch into readable text for the prompt
	formatted_batch = ""
	for idx, lead in enumerate(batch):
		formatted_batch += f"Lead {idx + 1}:\nCompany: {lead['Company']}\nExecutive: {lead['First Name']} {lead['Last Name']}\nJob Title: {lead['Job Title']}\nIndustry: {lead['Industry']}\n\n"

	prompt = (
        f"You are given a batch of {len(batch)} leads. For each lead, generate a personalized outbound message "
        f"to the executive, introducing AI integration solutions to streamline their business processes. "
        f"Here are the details:\n\n{formatted_batch}"
        "For each lead, respond with a professional outbound message prefixed with the corresponding lead number."
    )

	try:
		# Configure the API key
		genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

		# Initialize the model
		model = genai.GenerativeModel('gemini-1.5-flash')

		# Make your first request to generate text
		response = model.generate_content(prompt)

		generated_content = response.text.split("Lead")
		
		for idx, message in enumerate(generated_content[1:], start=0):  # Skipping the empty first split
			batch[idx]["outbound message"] = "Lead" + message.strip()

		# Print the generated content
		return batch

	except HTTPError as http_err:
		print(f"HTTP error occurred: {http_err}")
	except ConnectionError as conn_err:
		print(f"Connection error occurred: {conn_err}")
	except Timeout as timeout_err:
		print(f"Timeout error occurred: {timeout_err}")
	except RequestException as req_err:
		print(f"An error occurred: {req_err}")
	except KeyError as key_err:
		print("API key not found. Make sure it's set correctly in the environment variables.")    

print(lead_info)
# get batches from lead info
batches = get_batches(lead_info)
print(batches)
# loop through each batch and update the leads
def batch_processing(batches):
	for batch in batches:
		batch = generate_response(batch)
		time.sleep(60)
	return batches

batches = batch_processing(batches)
merged_list = [item for sublist in batches for item in sublist]
#Update the leads to the database
update_leads(merged_list)
