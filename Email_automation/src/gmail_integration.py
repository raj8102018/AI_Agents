import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
#SCOPES = ["https://mail.google.com/"]


def authenticate_gmail_api():
    """Authenticate and return the Gmail API service."""
    creds = None
    # Check if token.json exists to load credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If credentials are not valid, perform the authorization flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def gmail_send_message(service):
    """Create and send an email message and print the returned message ID."""
    try:
        message = EmailMessage()
        message.set_content("make a mental click!!!!!!!!")
        message["To"] = "mrohithg@gmail.com"
        message["From"] = "yuvraj07102024@gmail.com"
        message["Subject"] = "Sent from EMAIL AUTOMATION AGENT"

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        # Send the email
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def show_chatty_threads():
    
    """Display threads with long conversations (>= 3 messages).
    
    Returns: tuple (list of unread_mails, list of chatty_threads)
    """
    try:
        # Authenticate and get the service
        service = build("gmail", "v1", credentials=Credentials.from_authorized_user_file("token.json", SCOPES))
        
        # Fetch list of messages in the inbox
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1000).execute()
        messages = results.get('messages', [])
        
        unread_mails = []
        chatty_threads = []
        thread_message_counts = {}

        for message in messages:
            full_message = service.users().messages().get(userId='me', id=message['id']).execute()

            # Check if the message is unread
            if 'labelIds' in full_message and 'UNREAD' in full_message['labelIds']:
                unread_mails.append(full_message)

            # Check if the message belongs to a thread
            thread_id = full_message.get('threadId', None)
            if thread_id:
                # Increment the message count for the thread
                if thread_id not in thread_message_counts:
                    thread_message_counts[thread_id] = [full_message]  # Start a new list of messages for this thread
                else:
                    thread_message_counts[thread_id].append(full_message)  # Add message to the existing thread

        # Now, filter threads with 3 or more messages
        for thread_id, thread_messages in thread_message_counts.items():
            if len(thread_messages) >= 3:
                chatty_threads.append({
                    'threadId': thread_id,
                    'messages': thread_messages
                })

        return unread_mails, chatty_threads

    except HttpError as error:
        print(f"An error occurred: {error}")

def process_email_data():

    extracted_info = []

    emails = show_chatty_threads()[0]

    for email in emails:
        # Extract email information
        email_data = {
            "id": email.get("id"),
            "threadId": email.get("threadId"),
            "labelIds": email.get("labelIds", []),
            "snippet": email.get("snippet"),
            "from": None,
            "subject": None,
            "date": None,
            "message_id": None,
            "in_reply_to": None,
            "references": None
        }

        # Extract headers from the payload
        if "payload" in email and "headers" in email["payload"]:
            for header in email["payload"]["headers"]:
                if header["name"].lower() == "from":
                    email_data["from"] = header["value"]
                elif header["name"].lower() == "subject":
                    email_data["subject"] = header["value"]
                elif header["name"].lower() == "date":
                    email_data["date"] = header["value"]
                elif header["name"].lower() == "message-id":
                    email_data["message_id"] = header["value"]
                elif header["name"].lower() == "in-reply-to":
                    email_data["in_reply_to"] = header["value"]
                elif header["name"].lower() == "references":
                    email_data["references"] = header["value"]

        # Classify the action based on email's labels and snippet content
        action = categorize_email(email_data)
        email_data["action"] = action

        extracted_info.append(email_data)

    return extracted_info

def categorize_email(email_data):
    # Categorize emails based on certain conditions (can be modified)
    if "INBOX" in email_data["labelIds"]:
        if "UNREAD" in email_data["labelIds"]:
            if re.search(r"(urgent|asap|important)", email_data["snippet"], re.I):
                return "fetch_response"
            elif re.search(r"(follow up|reminder)", email_data["snippet"], re.I):
                return "write_followup"
        else:
            if email_data["from"]:
                return "categorize"
    return "no_action"


if __name__ == "__main__":
    service = authenticate_gmail_api()  # Authenticate and get the service
    gmail_send_message(service)  # Send the email
    #print(process_email_data())



    