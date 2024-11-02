import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import time
import json
import textwrap

from mongodb_integration import leads_for_initial_contact
from email_response_generation import get_batches, get_summary, generate_response, process_email_batch_optimized
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send", 'https://www.googleapis.com/auth/gmail.modify', "https://www.googleapis.com/auth/calendar.readonly"]
#SCOPES = ["https://mail.google.com/"]

#to authenticate with the gmail api. might open a window for consent during the first run
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

#to send an email
def gmail_send_message(sender,recepient,subject,content):
    """Create and send an email message and print the returned message ID."""
    try:
        service = authenticate_gmail_api()
        message = EmailMessage()
        content = content.replace("\\n", "\n").replace("\n", "\n")
        message.set_content(content)
        message["To"] = recepient
        message["From"] = sender
        message["Subject"] = subject

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        # Send the email
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")

#to send a reply to an email received
def gmail_reply_message(sender,recepient,subject,content,message_id,thread_id):
    """Create and send an email message and print the returned message ID."""
    try:
        message_id = message_id
        thread_id = thread_id
        service = service = authenticate_gmail_api()
        message = EmailMessage()
        content = content.replace("\\n", "\n").replace("\n", "\n")
        message.set_content(content)
        message["To"] = recepient  # Recipient's email
        message["From"] = sender  # Your email
        message["Subject"] = f"Re: {subject}"  # Use 'Re:' for replies
    
        # Set the In-Reply-To header
        message["In-Reply-To"] = message_id
        
        # Optional: Set References header (may help with threading)
        message["References"] = message["In-Reply-To"]

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            "raw": encoded_message,
            "threadId": thread_id  # Thread ID
        }

        # Send the email
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")

#to initiate converstation in batch using initially composed customized outbound message stored in MongoDB
def batch_mail_initiation(batch_size=1):
    authenticate_gmail_api()
    leads_to_contact = leads_for_initial_contact()
    sender = 'yuvraj07102024@gmail.com'
    
    for i in range(0,len(leads_to_contact),batch_size):
        batch = leads_to_contact[i:i+batch_size]
    # gmail_send_message(sender,recepient,subject,content):
        for entry in batch:
            gmail_send_message(sender,entry['recepient'],entry['subject'],entry['content'])
            print('sent...'+str(len(batch)))
        time.sleep(5)
    print('successfully sent')

def extract_emails_regex(content):
        # Use regular expression to match "Email n" followed by the email body
        email_pattern = r"\*\*Email\s(\d+):\*\*(.*?)(?=\*\*Email|\Z)"
        
        # Find all matches with the pattern 
        matches = re.findall(email_pattern, content, re.DOTALL)
        print(matches)
        # Convert matches into the desired dictionary format
        responses = {int(number): body.strip() for number, body in matches}
        
        return responses
 
    
#to genenrate follow up messages for a batch of emails for replying in bulk
def generate_batch_response_for_bulk_reply(response_parameters):
    
    batch = get_batches(response_parameters)
    
    summaries = get_summary(batch)
    
    cleaned_summaries = re.sub(r"```json|```", "", summaries).strip()
    
    data_dict = json.loads(cleaned_summaries)
    
    print(data_dict)
        
    follow_up = generate_response(data_dict)
        
    return follow_up

def decode_base64(s):
    decoded_msg = base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))
    utf_msg = decoded_msg.decode('utf-8')
    return utf_msg

def show_chatty_threads():
    """Display threads with long conversations(>= 3 messages)
    Return: None

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    # creds, _ = google.auth.default()

    try:
        # create gmail api client
        service = authenticate_gmail_api()
        
        threads = (
            service.users().threads().list(userId="me", q="is:unread").execute().get("threads", [])
        )
        lengthy_threads = []

        for thread in threads:
            tdata = (
                service.users().threads().get(userId="me", id=thread["id"]).execute()
            )
            nmsgs = len(tdata["messages"])
            conversation = []
            only_received_msgs = []
            thread['threadId'] = thread["id"]
            is_last_msg_sent = False

            if nmsgs >= 2:
                messages = tdata['messages']
                
                for mssg in messages:

                    if 'labelIds' in mssg and 'UNREAD' in mssg['labelIds']:
                        thread['in_reply_to'] = mssg['id']
                    
                    if 'labelIds' in mssg and 'SENT' in mssg['labelIds']:
                        is_last_msg_sent = True
                    elif 'labelIds' in mssg and 'SENT' not in mssg['labelIds']:
                        is_last_msg_sent = False

                    if 'labelIds' in mssg and 'TRASH' in mssg['labelIds']:
                        # threads.remove(thread)
                        continue
                    
                    for header in mssg['payload']["headers"]:
                        if header["name"] == "Subject":
                            if not header['value'].startswith("Re: "):
                                thread['subject']= header["value"]
                        elif header["name"] == "Return-Path":
                            reply_to_email = header["value"]
                            if reply_to_email.startswith('<'):
                                reply_to_email = reply_to_email[1:]
                            if reply_to_email.endswith('>'):
                                reply_to_email = reply_to_email[:-1]
                            thread['recepient'] = reply_to_email
                            # thread["convo"] = msg
                        elif header["name"] == "To":
                            thread['master_email'] = header["value"]
                        elif header["name"].lower() == "date":
                            thread["date"] = header["value"]
                        elif header["name"].lower() == "message-id":
                            thread["message_id"] = header["value"]
                        elif header["name"].lower() == "in-reply-to":
                            thread["in_reply_to"] = header["value"]
                        elif header["name"].lower() == "references":
                            thread["references"] = header["value"]

                    body = mssg['payload']['body']
                    if(body['size']!=0):
                        conversation.append(decode_base64(body['data']))
                    else:
                        parts = mssg['payload']['parts']
                        for part in parts:
                            if part['mimeType']=='text/plain':
                                conversation.append(decode_base64(part['body']['data']))
                                only_received_msgs.append(conversation[-1])
                thread['conversation'] = conversation
                thread['only_received_msgs'] = only_received_msgs
                
                
                if not is_last_msg_sent:
                    lengthy_threads.append(thread)
                # return lengthy_threads
            
            
        return lengthy_threads

    except HttpError as error:
        print(f"An error occurred: {error}")

from langchain_integration import overall_simple_chain        
        
def batch_reply():
    # req_details = extract_req_details()
    post_data = { "addLabelIds": [
                    ],
                "removeLabelIds": [
                    "UNREAD"
                    ]
                }
    req_details = show_chatty_threads()
    if len(req_details) > 0:
        response_parameters = [{'subject' : entry['subject'], 'conversation':entry['conversation'], 'date': entry['date']} for entry in req_details]
        batch = get_batches(response_parameters)
        first_data_input = {"input": json.dumps(batch)}  # Changed "first_entries" to "input"
        follow_up_details = overall_simple_chain.run(first_data_input)
       
        print(follow_up_details)
        print()
        prefix = r'```json(\n)*'
        suffix = r'```(\n)*'

        follow_up_details = re.sub(suffix+prefix, ",", follow_up_details)
        follow_up_details = re.sub(prefix, "[", follow_up_details)
        follow_up_details = re.sub(suffix, "]", follow_up_details)

        # print(follow_up_details)
        follow_up_details_arr = json.loads(follow_up_details)  
        dict_to_schedule = follow_up_details_arr[1]
        dict_followups = follow_up_details_arr[0]
        dict_leadstorespond = follow_up_details_arr[2]
        # print("dict_followup:", dict_followups)
        # print("dict to schedule:", dict_to_schedule)
        # print("dict to close:", dict_leadstorespond)

        service = authenticate_gmail_api()
        for idx, entry in enumerate(req_details,start = 1):
            index = str(idx)
            if index in dict_leadstorespond.keys():
        # gmail_reply_message(sender,recepient,subject,content,message_id,thread_id):
                gmail_reply_message(entry['master_email'],entry['recepient'],entry['subject'],dict_leadstorespond[index],entry['message_id'],entry['threadId'])
                service.users().threads().modify(userId="me", id=entry['threadId'], body=post_data).execute()
            elif index in dict_followups or dict_to_schedule:
                service.users().threads().modify(userId="me", id=entry['threadId'], body=post_data).execute()
        print("success")
    else:
         return

if __name__ == "__main__":  
    batch_reply()
    # batch_mail_initiation()    