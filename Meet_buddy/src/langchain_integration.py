import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain

import warnings
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
    "If the client asks for more time before responding or requests to be contacted after a month, indicate that the follow-up will be postponed and include a note stating that the lead is in follow-up. "
    "This summary will be used to draft a follow-up response for each conversation. "
    "Return the output as a JSON object with the email number (integer only) as the key and the conversation summary as the value. "
    "Include the date from the provided data at the end of each summary in the exact format it appears in the batch data. Mention it as the last message received on: date. "
    "For context, your name is Yuvraj, and your company is QState."
)

# Define the second prompt template
second_prompt = PromptTemplate.from_template(
    "You are an AI tasked with classifying email conversation threads between a client and a business sales executive. "
    "Here are the entries: {summaries}. Each entry includes a summary and a date. "
    "Your task is to classify each entry into three separate JSON objects:\n\n"
    
    "1. **Follow-up Leads**: For entries that indicate the lead is currently in follow-up, create a JSON object with the entry ID as the key and the summary as the value.\n"
    
    "2. **Meeting Scheduled Leads**: For entries where the client has mentioned a specific meeting time, create another JSON object with the entry ID as the key and include both the summary and date in the value.\n"
    
    "3. **Follow-up Suggestions**: For remaining entries, if the client has rejected the offer just draft a polite reply or else generate a follow-up email body that acknowledges the client’s interest, reiterates key points from the summary, and requests their availability for further discussion. "
    "Create a JSON object with the entry ID as the key and the follow-up email text as the value. \n\n"
    
    "Return only the three JSON objects, without any additional text."
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



