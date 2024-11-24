"""
This module is to make api calls, fetch responses and conduct batch processing
"""
import sys
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException # pylint: disable=redefined-builtin

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


# from config.settings import GOOGLE_API_KEY

# Load environment variables from .env file
load_dotenv()


def generate_response(batch):
    """This function makes the api call and formats the response into the required format"""
    # Format the batch into readable text for the prompt
    formatted_batch = ""
    for idx, lead in enumerate(batch):
        formatted_batch += (
			f"Lead {idx + 1}:\n"
			f"Company: {lead['Company']}\n"
			f"Executive: {lead['First Name']} {lead['Last Name']}\n"
			f"Job Title: {lead['Job Title']}\n"
			f"Industry: {lead['Industry']}\n\n"
		)

    prompt = (
    f"You are given a batch of {len(batch)} leads. For each lead, generate a personalized outbound message "
    "to the executive, introducing AI integration solutions to streamline their business processes. "
    f"Here are the details:\n\n{formatted_batch}"
    "For each lead, respond with a professional outbound message in the following format:\n"
    "For context, your name is Yuvraj, and your company is QState."
    "Subject: [Subject Line]\n"
    "[Message body]"
    )


    try:
        # Configure the API key
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Make your first request to generate text
        response = model.generate_content(prompt)
        print('-----------------')
        print(response.text)
        print('-----------------')

        if not response.text:
            raise ValueError("The model response is empty.")
        
        generated_content = response.text.split("Lead")
        if len(generated_content) == 1:
            generated_content.insert(0, "**")
        if len(generated_content[1:]) != len(batch):
            raise ValueError("Mismatch between generated messages and leads.")
        # raise ValueError("No Mismatch between generated messages and leads.")
        for idx, message in enumerate(generated_content[1:], start=0):
            batch[idx]["outbound message"] = "Lead" + message.replace('**', '').strip()

        # Assign default message for any leads without an outbound message
        for lead in batch:
            if "outbound message" not in lead:
                lead["outbound message"] = "No outbound message generated."

        # for idx, message in enumerate(
        #     generated_content[1:], start=0
        # ):  # Skipping the empty first split
        #     batch[idx]["outbound message"] = "Lead" + message.replace('**','').strip()
        # return batch

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except KeyError as key_err: # pylint: disable=unused-variable
        print("API key not found. Make sure it's set correctly in the environment variables.")


# loop through each batch and update the leads
def batch_processing(batches_to_process):
    """This function processes the batches in time intervals"""
    print("batch_processing started")
    for batch in batches_to_process:
        print("going into generate_response")
        batch = generate_response(batch)
        time.sleep(10)
    return batches_to_process
