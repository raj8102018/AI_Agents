import io
from pymongo import MongoClient
from pymongo import UpdateOne
from Config.settings import MONGODB_URI, MONGODB_DB #pylint: disable=wrong-import-position
from bson.objectid import ObjectId

def connect_to_mongodb():
    """This function contains the logic to connect to database"""
    # Use the MongoDB URI from the settings
    client = MongoClient(MONGODB_URI)
    # Access the specific database
    db = client[MONGODB_DB]
    return db


def store_pdf_in_mongodb(user_id,pdf_file):
    """Store PDF in MongoDB"""
    pdf_bytes = pdf_file.read()
    database = connect_to_mongodb()
    pdf_collection = database["ragfiles"]
    pdf_collection.insert_one({"file_name": pdf_file.name, "pdf_data": pdf_bytes,"user_id": ObjectId(user_id)})
    print(f"PDF {pdf_file.name} stored in MongoDB.")
    # Logic to handle file input, PDF text extraction, and conversational chain processing
    # pdf_name = "part_b.pdf"  # Modify to handle file input from your backend

    # Open the PDF file and pass the file object to the function
    # with open(pdf_name, 'rb') as pdf_file:
    # store_pdf_in_mongodb(pdf_file)  # Pass the opened file object


def get_pdf_from_mongodb(pdf_name):
    """Fetch the PDF from MongoDB by file name"""
    database = connect_to_mongodb()
    pdf_collection = database["ragfiles"]
    pdf_doc = pdf_collection.find_one({"file_name": pdf_name})
    if pdf_doc:
        pdf_bytes = pdf_doc["pdf_data"]
        return io.BytesIO(pdf_bytes)  # Return as BytesIO object to be processed
    print(f"No PDF found with name {pdf_name} in MongoDB.")
    return None