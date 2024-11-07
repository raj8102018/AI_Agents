"""This module contains the functionality for generating responses using GEMINI API"""
#pylint: disable=line-too-long
#pylint: disable=unused-variable

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException #pylint: disable=redefined-builtin

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "src")))

# Load environment variables from .env file
load_dotenv()


def get_batches(data, batch_size=1):
    """# function for generating batches to feed LLM"""
    batches = []
    list_length = len(data)

    if list_length == 0:
        return []  # or another appropriate response

    for i in range(0, list_length, batch_size):
        batches.append(data[i : i + batch_size][0])  # Slice directly

    return batches


def process_email_batch_optimized(batch):
    """Function to format the batches into text for to reduce complexity of the input to LLM"""
    result = []

    for idx, email in enumerate(batch, 1):
        subject = email.get("subject", "No Subject")

        # Join the entire conversation for each email at once
        conversation_text = "\n".join(email.get("conversation", []))

        date = "".join(email.get("date", []))

        # Create the formatted email thread text
        formatted_email = f"Email {idx}:\nSubject: {subject}\nSummary:\n{conversation_text}\ndate:\n{date}\n"

        result.append(formatted_email)

    return "\n".join(result)


def process_email_batch_summaries_optimized(data):
    """Function for creating batches of summaries"""
    result = []

    for idx, (email_num, conversation) in enumerate(data.items(), 1):
        subject = f"Follow-up regarding AI solutions discussion with client {idx}"  # Customize the subject line if needed

        # Create the formatted email thread text
        formatted_email = (
            f"Email {email_num}:\nSubject: {subject}\nConversation:\n{conversation}\n"
        )

        result.append(formatted_email)

    return "\n".join(result)


def generate_response(batch):
    """# function to generate response from the LLM"""
    formatted_batch = process_email_batch_summaries_optimized(batch)

    prompt = (
        f"You are given {len(batch)} email conversation threads between a client and a business sales executive. "
        f"Each entry includes a subject line that indicates the context, followed by a summary of the exchange between the two parties. "
        f"The data is formatted as follows: {formatted_batch}. "
        f"Your task is to classify the data into three separate JSON objects, no single entry can be classfied into more than one JSON object"
        f"1. **First JSON Object**: Identify entries where the summary indicates that the lead is currently in follow-up. "
        f"Place these entries in the first JSON object with their summaries exactly as-is and only note the email number (integer) as the key. "
        f"2. **Second JSON Object**: From the remaining entries, identify those where a specific meeting time is mentioned by the client. "
        f"Place these entries in the second JSON object, retaining the original summary and date as-is. "
        f"3. **Third JSON Object**:"
        f"   - for the remaining entries, go throught the summary carefully, generate a personalized follow-up email body that acknowledges the client’s interest and confirms general details, "
        f"     briefly reiterates key discussion points, and asks for the client’s availability for further discussion. "
        f"   - Do not include the subject line or any redundant information already evident from the summary. Use only the email number (integer) as the key."
        f"Return all three JSON objects only, with the email number as the key in each case, without any prefixes or 'Email' notation. "
    )

    try:
        # Configure the API key
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")

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
        print(
            "API key not found. Make sure it's set correctly in the environment variables."
        )


def get_summary(batch):
    """Function to fetch summaries of conversations"""
    formatted_batch = process_email_batch_optimized(batch)

    prompt = (
        f"You are given {len(batch)} email conversation threads between a client and a business sales executive."
        f" Each conversation includes a subject line providing context, a message exchange between the two parties, and a date."
        f" The data is formatted as follows: {formatted_batch}."
        f" Summarize each conversation into a concise paragraph, specifying who provided each piece of information."
        f" Each summary should highlight key points, exchanges, and any action items, clearly labeling client and executive contributions."
        f" If the client asks for more time before responding or requests to be contacted after a month, indicate that the follow-up will be postponed and include a note stating that the lead is in follow-up."
        f" This summary will be used to draft a follow-up response for each conversation."
        f" Return the output as a JSON object with the email number (integer only) as the key and the conversation summary as the value."
        f" Include the date from the provided data at the end of each summary in the exact format it appears in the batch data. Mention it as the last message received on: date "
        f" For context, your name is Yuvraj, and your company is QState."
    )

    try:
        # Configure the API key
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")

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
        print(
            "API key not found. Make sure it's set correctly in the environment variables."
        )


if __name__ == "__main__":
    pass
