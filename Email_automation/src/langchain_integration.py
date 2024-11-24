"""
This module contains the functionality for Langchain framework related usage
"""

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=missing-timeout

import warnings
import os
from dotenv import load_dotenv
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables import chain

warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv()

# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not GOOGLE_API_KEY:
    raise ValueError("Google API key is not set. Please check your .env file.")

# Initialize the Google Generative AI model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0
)

# Define the first prompt template
first_prompt = PromptTemplate.from_template( 
    "You are given email conversation threads between a client and a business sales executive."
    "Here are the entries: {input}."
    "Each entry includes a subject line providing context, a message exchange between the two parties, and a date."
    "Summarize each conversation into a concise paragraph, specifying who provided each piece of information."
    "Each summary should highlight key points, exchanges, and any action items, clearly labeling client and executive contributions."
    "Only if the client asks for more time before responding or requests to be contacted after a month, indicate that the follow up will be postponed and include a note stating that the lead is in follow up."
    "This summary will be used to draft a follow up response for each conversation."
    "Return the summary and indicate whether the conversation contains a question."
    "The result should be formatted as two JSON objects, where the key is the email number (integer only), and the value contains:"
    "The conversation summary."
    "A 'has_query' field that indicates whether the conversation contains a question from the client."
    "If the conversation contains a question, set 'has_query': true. Exclude the queries regarding timings of the meeting or a call and set 'has_query' : false for them."
    "If not, set 'has_query': false."
    "A 'Last message received on' field with [date] from the provided data.'"
    "For context, your name is Yuvraj, and your company is QState."
    "The two json objects should have the following format: 'with_queries' field having entries with queries i.e 'has_query': true and 'without_queries' i.e 'has_query': false field with remaiing entries"
    "wrap both the json objects in a value with key 'summaries'"
    "Ensure the output is plain JSON without any Markdown formatting or code block delimiters."
    "pack all the data as a value with key 'summaries'"
    "Strictly follow the guidelines about segregating the emails into with and without queries"
)

refinement_prompt = PromptTemplate.from_template(
    "You are given a set of conversation summaries from previous email exchanges between clients and sales executives."
    "Here are the summaries: {summaries}"
    "The summaries are grouped as 'with_queries' and 'without_queries' Each summary includes a conversation summary, whether there is a query, and the last message received on a specific date."
    "Each summary includes a conversation summary, whether there is a query, and the last message received on a specific date."
    "Your task is to take strictly only the summaries grouped under 'without_queries' and segregate each entry into one of three types of responses and return the collections, strictly following these rules:\n\n"
    "1. **Meeting Scheduled**: For entries where the client has confirmed or proposed a specific time for a meeting or a call, add it to the 'Meeting Scheduled' json object. Use the entry ID as the key, and include both the conversation_summary and 'Last message received on' in the value.\n\n"
    "2. **Recontact Needed**: For entries where the client explicitly requests to be contacted at a later date, such as 'Please follow up after a month,' add it to the 'Recontact Needed' json object. Use the entry ID as the key, with the conversation_summary as the value., calculate follow_up date from 'last message received on' field entry and details from the summary and include it\n\n"
    "3. **Follow up Suggested**: For all remaining entries, carefully generate a follow up email acknowledging the client’s interest, restating key points, and requesting their availability for further discussion.For greeting questions, include the polite response. if the client has declined the offer, generate a polite closing message. Add these to the 'Follow up Suggested' json object, with the entry ID as the key and the generated email body as the value. Do not return the subject. for your context, you are 'yuvraj, the sales executive'\n\n"
    "Ensure each entry is assigned to **only one** category, based on the first applicable rule: prioritize 'Meeting Scheduled' over 'Recontact Needed,' and 'Recontact Needed' over 'Follow up Suggested.'\n\n"
    "Return only these three json objects in this exact order with the content: 1, 2, and 3. "
    "Do not include any place holders or mention that you have attached anything with the response"
    "Return only the json objects directly, without any category labels or additional text."
    "Strictly Ensure the output is plain json without any Markdown formatting or code block delimiters."
)
llm_chain_summary = LLMChain(llm=llm, prompt=first_prompt)

# Second chain: Extracting the query from the conversation summary (expects 'summaries' as input)
refinement_chain = LLMChain(
    llm=llm, prompt=refinement_prompt, output_key="processed_entries"
)

# Sequential chain to run both summarizing and query extraction in sequence
first_thread = SimpleSequentialChain(
    chains=[llm_chain_summary, refinement_chain],  # Chain two LLM chains together
)

query_extraction_prompt = PromptTemplate.from_template(
    """
You are given a set of conversation summaries from previous email exchanges between clients and sales executives.
Here are the summaries: {summaries}

The summaries are grouped as 'with_queries' and 'without_queries'. Each summary includes a conversation summary, whether there is a query, and the last message received on a specific date.

Your task is to take only the summaries grouped under 'with_queries' and extract the query from each summary, if present. For each summary:
- If there is a query from the client, extract the exact question that the client has asked and frame it properly for Retrieval Augmented Generation.
- If there is no query, skip it and do not include it in the JSON for extracted queries.
- never include a query from the client
The output should contain one JSON objects:
1. The first key `questions`, with an inner object where:
        - The email number (integer only, starting from 1) is the key.
        - The extracted query is the value (only if a query is present).
2. The key `summaries`, with an inner object where:
        - The email number (integer only, starting from 1) is the key.
        - The conversation summary with the 'Last message received on' field value as the value.
    - Ensure there are no newline characters in between or after the dictionaries.

Ensure the output is plain JSON without any Markdown formatting or code block delimiters. For context, your name is Yuvraj and you are the sales executive, and your company is QState.
"""
)

postquery_refinement_prompt = PromptTemplate.from_template(
    "You are given a set of conversation summaries and answers from previous email exchanges between clients and sales executives."
    "here is the data: {entries}"
    "Return the output in the following format: "
    "Each entry includes a conversation summary followed by answer to the quesiton in it."
    "Your task is go through each and every entry along with the answer, even if the client has declined the offer, generate a polite closing message. For other entries, generate a follow up email acknowledging the client’s interest, restating key points, and requesting their availability for further discussion. Add these to the 'Follow up Suggested' JSON object, with the entry ID as the key and the generated email body as the value. for your context, you are 'yuvraj, the sales executive'. Do not return the subject\n\n"
    "Make sure to include the answer provided"
    "Return three json objects in this exact order:"
    "1. **Meeting Scheduled**: empty json"
    "2. **Recontact Needed**: empty json"
    "3. **Follow up Suggested**: A json object with entry id(integer only) and the email bodies without subject."
    "Return the JSON objects directly, without any category labels or additional text."
    "Ensure the output is plain JSON without any Markdown formatting or code block delimiters or new line characters. For context"
    "Return only the json directly, without any category labels or additional text."
    "Do not include any place holders or mention that you have attached anything with the response"
    "Ensure the output is plain json without any Markdown formatting or code block delimiters."
    "Ensure response to all the items in the {entries}"
    "pack all the three json items in a json"
)


llm_chain_query_extraction = LLMChain(llm=llm, prompt=query_extraction_prompt)

# Sequential chain: Extract summary, then queries, and fetch answers
second_thread = SimpleSequentialChain(
    chains=[llm_chain_summary, llm_chain_query_extraction]
)

postquery_refinement_chain = LLMChain(llm=llm, prompt=postquery_refinement_prompt)


@chain
def get_query_answer(questions, company="QState"):
    "get answer from document for the query"
    print("fetching answers")
    url = "http://127.0.0.1:5000/api/answer"
    data = {"question": questions, "file_name": f"{company}.pdf"}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        return response.json()
    return ("Failed:", response.status_code, response.text)


# Define a custom function to ensure only the processed entries are returned
class CustomRunnableParallel(RunnableParallel):
    """ Class to create a custom parallel chain to retrieve the output excluding the input text"""
    def invoke(self, inputs):
        """ To get the result from the chain"""
        result = super().invoke(inputs)

        # Extract the relevant outputs from both threads
        final_result = {
            "first_thread": result.get("first_thread", {}).get("output", {}),
            "second_thread": result.get("second_thread", {}).get("output", {}),
        }

        return final_result


# Create the customized parallel chain
parallel_chain = CustomRunnableParallel(
    first_thread=first_thread, second_thread=second_thread
)


def group_summaries_and_answers(input_data):
    """The function to group summaries and answers in the output"""
    summaries = input_data["summaries"]
    answers = eval(input_data["answers"])  # Safely parse the string into a dictionary

    result = {}

    # Iterate through the summaries and match with the corresponding answer using the index
    for index in summaries:
        result[index] = (
            summaries[index] + " " + answers.get(index, "Answer not available")
        )

    return result
