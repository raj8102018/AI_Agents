import os
from dotenv import load_dotenv
import google.generativeai as genai
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

#import extract_req_details
from gmail_integration import extract_req_details

# Load environment variables from .env file
load_dotenv()

prompt = "write few quotes each from ayn rands fountainhead and a man called ove by fredrick backman"
# mail_batch = []
# imp_keys_dict = {}
#         imp_keys_dict['threadId'] = thread_dict['threadId']
#         imp_keys_dict['master_email'] = re.search(email_regex, thread_dict['snippet']).group()
#         imp_keys_dict['recepient'] = thread_dict['from']
#         imp_keys_dict['labels'] = thread_dict['labelIds']
#         imp_keys_dict['subject'] = thread_dict['subject']
#         imp_keys_dict['message_id'] = thread_dict['message_id']
#         imp_keys_dict['conversation'] = thread_dict['conversation']
#         imp_keys_dict['entry_no'] = counter + 1
# gmail_reply_message(sender,recepient,subject,content,message_id,thread_id):

req_details = extract_req_details()

response_parameters = [{'subject' : entry['subject'], 'conversation':entry['conversation']} for entry in extract_req_details()]

def get_batches(data, batch_size=1):
	batches = []
	list_length = len(data)

	if list_length == 0:
		return []  # or another appropriate response

	for i in range(0, list_length, batch_size):
		batches.append(data[i:i + batch_size][0])  # Slice directly

	return batches

def generate_response(batch):
    try:
        # Configure the API key
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Make your first request to generate text
        response = model.generate_content(prompt)

        # Print the generated content
        print(response.text)

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


if __name__ == "__main__":
    batches = get_batches(response_parameters)
    print(batches)
