import os
from dotenv import load_dotenv
import google.generativeai as genai
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

# Load environment variables from .env file
load_dotenv()

#function for generating batches to feed LLM
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
        
        date = "".join(email.get('date', []))
        
        # Create the formatted email thread text
        formatted_email = f"Email {idx}:\nSubject: {subject}\nSummary:\n{conversation_text}\ndate:\n{date}\n"
        
        result.append(formatted_email)
    
    return "\n".join(result)


def process_email_batch_summaries_optimized(data):
    result = []
    
    for idx, (email_num, conversation) in enumerate(data.items(), 1):
        subject = f"Follow-up regarding AI solutions discussion with client {idx}"  # Customize the subject line if needed
        
        # Create the formatted email thread text
        formatted_email = f"Email {email_num}:\nSubject: {subject}\nConversation:\n{conversation}\n"
        
        result.append(formatted_email)
    
    return "\n".join(result)


#function to generate response from the LLM
def generate_response(batch):
    formatted_batch = process_email_batch_summaries_optimized(batch)
    # prompt = (f"You are given {len(batch)} email conversation threads between a client and a business sales executive."
    #       f" Each conversation contains a subject line indicating the context and a message exchange between the two parties."
    #       f" The data is formatted as follows: {formatted_batch}."
    #       f" For each conversation, analyze the subject and content, then write a follow-up email body (excluding the subject line)."
    #       f" Return the output as a JSON object with the email number (integer only) as the key and the follow-up email body as the value."
    #       f" Your name is Yuvraj and your company name is QState")
    
    # prompt = (
    # f"You are given {len(batch)} email conversation threads between a client and a business sales executive. "
    # f"Each conversation includes a subject line that indicates the context, followed by a message exchange between the two parties. "
    # f"The data is formatted as follows: {formatted_batch}. "
    # f"For each conversation, analyze the subject and content carefully, then write a personalized follow-up email body (excluding the subject line). "
    # f"Ensure your response acknowledges the client's interest, confirms the meeting details, and briefly reiterates key points of discussion. "
    # f"Do not repeat any redundant information that is already evident from the summaries provided. "
    # f"Additionally, do not include any placeholders for links or documents, as this will be managed by another agent. "
    # f"Return the output as a JSON object with the email number (integer only) as the key and the follow-up email body as the value. "
    # f"Your name is Yuvraj, and your company is QState.")
    
    # prompt = (
    #     f"You are given {len(batch)} email conversation threads between a client and a business sales executive. "
    #     f"Each conversation includes a subject line that indicates the context, followed by a summary of the exchange between the two parties. "
    #     f"The data is formatted as follows: {formatted_batch}. "
    #     f"For each conversation, go through the subject and message summary carefully, and separate them as follows: "
    #     f"1. If a specific time is mentioned by the client for a meeting, include that conversation without the subject as-is in a JSON object without modifying the content. do not remove the date."
    #     f"2. For entries without a specified meeting time, write a personalized follow-up email body (excluding the subject line). "
    #     f"In each follow-up, acknowledge the client’s interest, confirm general details, and briefly reiterate key discussion points. "
    #     f"Additionally, for these entries without a meeting time, ask the client when they would be available to connect and discuss further. "
    #     f"Do not repeat any redundant information already evident from the summaries provided. "
    #     f"Also, do not include any placeholders for links or documents, as this will be managed by another agent. "
    #     f"Return the output as two JSON objects: the first containing entries with meeting times as provided, and the second with the customized follow-up email bodies based on the summaries. "
    #     f"Your name is Yuvraj, and your company is QState."
    # )
    
#     prompt = (
#     f"You are given {len(batch)} email conversation threads between a client and a business sales executive. "
#     f"Each conversation includes a subject line that indicates the context, followed by a summary of the exchange between the two parties. "
#     f"The data is formatted as follows: {formatted_batch}. "
#     f"For each conversation, go through the subject and message summary carefully, and separate them as follows: "
#     f"1. If a specific time is mentioned by the client for a meeting, include that conversation as-is in a JSON object without modifying the content and without removing the date. "
#     f"2. For entries without a specified meeting time from the client, write a personalized follow-up email body (excluding the subject line). "
#     f"In each follow-up, acknowledge the client’s interest, confirm general details, and briefly reiterate key discussion points. "
#     f"Additionally, for these entries without a meeting time, ask the client when they would be available to connect and discuss further. "
#     f"Do not repeat any redundant information already evident from the summaries provided. "
#     f"Also, do not include any placeholders for links or documents, as this will be managed by another agent. "
#     f"Return the output as two JSON objects: the first containing entries with meeting times as provided, and the second with the customized follow-up email bodies based on the summaries. "
#     f"For both JSON objects, use only the email number (integer) as the key, without any prefix or the word 'Email.' "
#     f"Your name is Yuvraj, and your company is QState."
# )
#     prompt = (
#     f"You are given {len(batch)} email conversation threads between a client and a business sales executive. "
#     f"Each conversation includes a subject line that indicates the context, followed by a summary of the exchange between the two parties. "
#     f"The data is formatted as follows: {formatted_batch}. "
#     f"For each conversation, review the subject and message summary carefully, and separate them as follows: "
#     f"1. If the client specifies a specific time for a meeting (Do not intrepret the date at the end of the summary as the suggested time), include that conversation as-is in a JSON object without modifying the content and keeping the date as provided or else return an empty json if there is no such entry. "
#     f"2. If there is no specific meeting time mentioned by the client, generate a personalized follow-up email body (excluding the subject line). "
#     f"In each follow-up, acknowledge the client’s interest, confirm general details, and briefly reiterate key discussion points. "
#     f"Additionally, for these entries, ask the client when they would be available to connect for a further discussion. "
#     f"Do not repeat any redundant information already evident from the summaries provided. "
#     f"Also, do not include placeholders for links or documents, as these will be managed by another agent. "
#     f"Return the output as two JSON objects: the first containing entries with valid meeting times as provided, and the second with the customized follow-up email bodies based on the summaries. "
#     f"For both JSON objects, use only the email number (integer) as the key, without any prefix or the word 'Email.' "
#     f"Your name is Yuvraj, and your company is QState."
# )
#     prompt = (
#     f"You are given {len(batch)} email conversation threads between a client and a business sales executive. "
#     f"Each entry includes a subject line that indicates the context, followed by a summary of the exchange between the two parties. "
#     f"The data is formatted as follows: {formatted_batch}. "
#     f"For each conversation, review the subject and message summary carefully, and separate them as follows: "
#     f"1. If the client specifies a specific time for a meeting (Do not interpret the date at the end of the summary as the suggested time), include that summary as-is in the JSON object only without modifying the content and keeping the date as provided, or else return an empty JSON if there is no such entry. "
#     f"2. If there is no specific meeting time mentioned by the client and generate a personalized follow-up email body (excluding the subject line) only if the summary doesn't indicate that the lead is in follow-up. "
#     f"In each follow-up, acknowledge the client’s interest, confirm general details, and briefly reiterate key discussion points. "
#     f"Additionally, for these entries, ask the client when they would be available to connect for a further discussion. "
#     f"3. If the summary indicates that the lead is now in follow-up, add that entry to a new JSON object without modifying its content. "
#     f"Do not repeat any redundant information already evident from the summaries provided. "
#     f"Also, do not include placeholders for links or documents, as these will be managed by another agent. "
#     f"Return the output as three JSON objects: the first containing entries with valid meeting times as provided, "
#     f"the second with the customized follow-up email bodies based on the summaries, and the third containing entries with leads now in follow-up. "
#     f"For all JSON objects, use only the email number (integer) as the key, without any prefix or the word 'Email.' "
#     f"Your name is Yuvraj, and your company is QState."
# )

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

def get_summary(batch):
    formatted_batch = process_email_batch_optimized(batch)
    
    # prompt = (f"You are given {len(batch)} email conversation threads between a client and a business sales executive."
    #       f" Each conversation includes a subject line providing context, a message exchange between the two parties, and a date."
    #       f" The data is formatted as follows: {formatted_batch}."
    #       f" Summarize each conversation into a concise paragraph, specifying who provided each piece of information."
    #       f" Each summary should highlight key points, exchanges, and any action items, clearly labeling client and executive contributions."
    #       f" This summary will be used to draft a follow-up response for each conversation."
    #       f" Return the output as a JSON object with the email number (integer only) as the key and the conversation summary as the value."
    #       f" Include the date from the provided data at the end of each summary in the exact format it appears in the batch data. Mention it as the last message received on: date "
    #       f" For context, your name is Yuvraj, and your company is QState.")
    
    prompt = (f"You are given {len(batch)} email conversation threads between a client and a business sales executive."
          f" Each conversation includes a subject line providing context, a message exchange between the two parties, and a date."
          f" The data is formatted as follows: {formatted_batch}."
          f" Summarize each conversation into a concise paragraph, specifying who provided each piece of information."
          f" Each summary should highlight key points, exchanges, and any action items, clearly labeling client and executive contributions."
          f" If the client asks for more time before responding or requests to be contacted after a month, indicate that the follow-up will be postponed and include a note stating that the lead is in follow-up."
          f" This summary will be used to draft a follow-up response for each conversation."
          f" Return the output as a JSON object with the email number (integer only) as the key and the conversation summary as the value."
          f" Include the date from the provided data at the end of each summary in the exact format it appears in the batch data. Mention it as the last message received on: date "
          f" For context, your name is Yuvraj, and your company is QState.")
    
 
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
    
  
if __name__ == "__main__":
    pass