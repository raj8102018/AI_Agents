import os
from dotenv import load_dotenv
import google.generativeai as genai
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

# Load environment variables from .env file
load_dotenv()

#function for generating batches to feed LLM
def get_batches(data, batch_size=1):
	batches = []
	list_length = len(data)

	if list_length == 0:
		return []  # or another appropriate response

	for i in range(0, list_length, batch_size):
		batches.append(data[i:i + batch_size][0])  # Slice directly

	return batches

#function to format the batches into text for to reduce complexity of the input to LLM
def process_email_batch_optimized(batch):
    result = []
    
    for idx, email in enumerate(batch, 1):
        subject = email.get('subject', 'No Subject')
        
        # Join the entire conversation for each email at once
        conversation_text = "\n".join(email.get('conversation', []))
        
        # Create the formatted email thread text
        formatted_email = f"Email {idx}:\nSubject: {subject}\nConversation:\n{conversation_text}\n"
        
        result.append(formatted_email)
    
    return "\n".join(result)

#function to generate response from the LLM
def generate_response(batch):
    formatted_batch = process_email_batch_optimized(batch)
    prompt = (f"You are given {len(batch)} email conversation threads between a client and a business sales executive."
          f" Each conversation contains a subject line indicating the context and a message exchange between the two parties."
          f" The data is formatted as follows: {formatted_batch}."
          f" For each conversation, analyze the subject and content, then write a follow-up email body (excluding the subject line)."
          f" Return the output as a JSON object with the email number (integer only) as the key and the follow-up email body as the value."
          f" Your name is Yuvraj and your company name is QState")
    try:
        # Configure the API key
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Make your first request to generate text
        response = model.generate_content(prompt)

        # Print the generated content
        return response.text

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

# def get_summary(chat_text):
#     prompt = (f"You are given {len(batch)} email conversation threads between a client and a business sales executive."
#           f" Each conversation contains a subject line indicating the context and a message exchange between the two parties."
#           f" The data is formatted as follows: {formatted_batch}."
#           f" For each conversation, analyze the subject and content, then write a follow-up email body (excluding the subject line)."
#           f" Return the output as a JSON object with the email number (integer only) as the key and the follow-up email body as the value."
#           f" Your name is Yuvraj and your company name is QState")
#     try:
#         # Configure the API key
#         genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

#         # Initialize the model
#         model = genai.GenerativeModel('gemini-1.5-flash')

#         # Make your first request to generate text
#         response = model.generate_content(prompt)

#         # Print the generated content
#         return response.text

#     except HTTPError as http_err:
#         print(f"HTTP error occurred: {http_err}")
#     except ConnectionError as conn_err:
#         print(f"Connection error occurred: {conn_err}")
#     except Timeout as timeout_err:
#         print(f"Timeout error occurred: {timeout_err}")
#     except RequestException as req_err:
#         print(f"An error occurred: {req_err}")
#     except KeyError as key_err:
#         print("API key not found. Make sure it's set correctly in the environment variables.")
    
    
if __name__ == "__main__":
    pass