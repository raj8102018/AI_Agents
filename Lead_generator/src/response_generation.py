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

# from config.settings import GOOGLE_API_KEY

# Load environment variables from .env file
load_dotenv()

def generate_response(lead):
    try:
        # Configure the API key
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        entry = [{key: value} for key, value in lead.items()]

        # Make your first request to generate text
        response = model.generate_content(f" based on the {entry} write a small outbound message asking if they are interested in ai automation in their business?")

        # Print the generated content

        lead['outbound message'] = response.text

        return lead

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


print(len(lead_info))
count = 0
for lead in lead_info: 
    if count % 15 == 0:
        print("maximum RPM reached for the tier: waiting for  a minute before updating the next batch")
        time.sleep(60)
        lead = generate_response(lead)
        update_leads(lead)
        count += 1
    else:
        lead = generate_response(lead)
        update_leads(lead)
        count += 1
    

