import os
from dotenv import load_dotenv
import google.generativeai as genai
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

# Load environment variables from .env file
load_dotenv()

prompt = "write few quotes each from ayn rands fountainhead and a man called ove by fredrick backman"

def generate_response(prompt):
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


generate_response(prompt)