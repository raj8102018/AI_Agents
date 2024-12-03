"""
This module contains the functionality for Langchain framework related usage
"""

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=missing-timeout

import warnings
import os
import json
from dotenv import load_dotenv
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables import chain
from .prompts import first_prompt, refinement_prompt, query_extraction_prompt, postquery_refinement_prompt

warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv()

# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
RAG_APP_DOMAIN_PATH = os.getenv("RAG_APP_DOMAIN_PATH")

# Check if the API key is set
if not GOOGLE_API_KEY:
    raise ValueError("Google API key is not set. Please check your .env file.")

# Initialize the Google Generative AI model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0
)

# Define the first prompt template
executive_name = "mpulelo mbangwa"
company_name = "essar industries"
first_prompt = PromptTemplate.from_template(first_prompt)

refinement_prompt = PromptTemplate.from_template(refinement_prompt)

llm_chain_summary = LLMChain(llm=llm, prompt=first_prompt)

# Second chain: Extracting the query from the conversation summary (expects 'summaries' as input)
refinement_chain = LLMChain(
    llm=llm, prompt=refinement_prompt, output_key="processed_entries"
)

# Sequential chain to run both summarizing and query extraction in sequence
first_thread = SimpleSequentialChain(
    chains=[llm_chain_summary, refinement_chain],  # Chain two LLM chains together
)

query_extraction_prompt = PromptTemplate.from_template(query_extraction_prompt)

postquery_refinement_prompt = PromptTemplate.from_template(postquery_refinement_prompt)


llm_chain_query_extraction = LLMChain(llm=llm, prompt=query_extraction_prompt)

# Sequential chain: Extract summary, then queries, and fetch answers
second_thread = SimpleSequentialChain(
    chains=[llm_chain_summary, llm_chain_query_extraction]
)

postquery_refinement_chain = LLMChain(llm=llm, prompt=postquery_refinement_prompt)


@chain
def get_query_answer(formatted_query):
    "get answer from document for the query"
    print("fetching answers")
    url = RAG_APP_DOMAIN_PATH
    parsed_query = json.loads(formatted_query)
    print(parsed_query)
    questions = parsed_query["questions"]
    company = parsed_query["company"]
    data = {"question": questions, "file_name": f"{company}.pdf"}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("it is working")
        print(response.json())
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
