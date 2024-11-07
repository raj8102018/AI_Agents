"""
This module contains the functionality for Langchain framework related usage
"""
#pylint: disable=line-too-long
#pylint: disable=no-name-in-module

import warnings
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain

warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not GOOGLE_API_KEY:
    raise ValueError("Google API key is not set. Please check your .env file.")

# Initialize the Google Generative AI model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0)

# Define the first prompt template
first_prompt = PromptTemplate.from_template(
    "You are given email conversation threads between a client and a business sales executive. "
    "Here are the entries: {first_entries}. Each entry includes a subject line providing context, a message exchange between the two parties, and a date. "
    "Summarize each conversation into a concise paragraph, specifying who provided each piece of information. "
    "Each summary should highlight key points, exchanges, and any action items, clearly labeling client and executive contributions. "
    "Only If the client asks for more time before responding or requests to be contacted after a month, indicate that the follow-up will be postponed and include a note stating that the lead is in follow-up. "
    "This summary will be used to draft a follow-up response for each conversation. "
    "Return the output as a JSON object with the email number (integer only) as the key and the conversation summary as the value. "
    "Include the date from the provided data at the end of each summary in the exact format it appears in the batch data. Mention it as the last message received on: date. "
    "For context, your name is Yuvraj, and your company is QState."
)

# Define the second prompt template
second_prompt = PromptTemplate.from_template(
    "You are an AI tasked with classifying email conversation threads between a client and a business sales executive. "
    "Here are the entries: {summaries}. Each entry includes a summary and a date. "
    "Your task is to classify each entry into one of three types of responses, strictly following these rules:\n\n"

    "1. **Meeting Scheduled**: For entries where the client has confirmed or proposed a specific time for a meeting, add it to the 'Meeting Scheduled' JSON object. Use the entry ID as the key, and include both the summary and date in the value.\n\n"

    "2. **Recontact Needed**: For entries where the client explicitly requests to be contacted at a later date, such as 'Please follow up after a month,' add it to the 'Recontact Needed' JSON object. Use the entry ID as the key, with the summary as the value.\n\n"

    "3. **Follow-up Suggested**: For all remaining entries, if the client has declined the offer, generate a polite closing message. For other entries, generate a follow-up email acknowledging the client’s interest, restating key points, and requesting their availability for further discussion. Add these to the 'Follow-up Suggested' JSON object, with the entry ID as the key and the generated email body as the value.\n\n"

    "Ensure each entry is assigned to **only one** category, based on the first applicable rule: prioritize 'Meeting Scheduled' over 'Recontact Needed,' and 'Recontact Needed' over 'Follow-up Suggested.'\n\n"

    "Return three JSON objects in this exact order: `Meeting Scheduled`, `Recontact Needed`, and `Follow-up Suggested`. "
    "If no entries match a category, return an empty JSON object for that category. "
    "Return only the JSON objects directly, without any category labels or additional text."
)



# Define the first chain: Summarization
summarization_chain = LLMChain(
    llm=llm,
    prompt=first_prompt
)

# Define the second chain: Classification
refinement_chain = LLMChain(
    llm=llm,
    prompt=second_prompt
)

# Create the sequential chain
overall_simple_chain = SimpleSequentialChain(
    chains=[summarization_chain, refinement_chain],
    verbose=True
)
