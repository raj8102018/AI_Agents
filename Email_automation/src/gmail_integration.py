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
import textwrap

from mongodb_integration import leads_for_initial_contact
from email_response_generation import get_batches, process_email_batch_optimized, generate_response
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
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


#to get threads in the inbox which are unread
def show_chatty_threads():
    
    """Display threads with long conversations (>= 3 messages).
    
    Returns: tuple (list of unread_mails, list of chatty_threads)
    """
    try:
        # Authenticate and get the service this way to avoid using it as a parameter
        #service = build("gmail", "v1", credentials=Credentials.from_authorized_user_file("token.json", SCOPES))
        service = authenticate_gmail_api()
       
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

#to process the data received from the show_chatty_threads function
def process_email_data():
    extracted_info = []
    
    # Fetch unread emails
    emails = show_chatty_threads()[0]

    # Prepare a dictionary to hold messages by thread ID
    threads_dict = {}

    for email in emails:
        thread_id = email.get("threadId")
        
        # If the thread ID is not already in the dictionary, initialize it
        if thread_id not in threads_dict:
            threads_dict[thread_id] = []

        conversation = []
        parts = email.get("payload").get("parts")
        for part in parts:
            s = part.get("body").get("data")
            decoded_msg = base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))
            # msg = decoded_msg.decode('utf-8')
            if(part.get("mimeType")=="text/plain"):
                msg = decoded_msg.decode('utf-8')
                conversation.append(msg)
        # Extract email information
        email_data = {
            "id": email.get("id"),
            "threadId": thread_id,
            "labelIds": email.get("labelIds", []),
            "snippet": email.get("snippet"),
            "conversation": conversation,
            "from": None,
            "subject": None,
            "date": None,
            "message_id": None,
            "in_reply_to": None,
            "references": None,
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

        # Add the current email data to the list of messages in the thread
        if thread_id in threads_dict:
            threads_dict[thread_id].append(email_data)
        else:
            threadss_dict[thread_id] = [email_data]

    # Convert the threads dictionary to a list of extracted info
    for thread_id, messages in threads_dict.items():
        extracted_info.append(messages)


    # email_threads = show_chatty_threads_2()
    # for email_thread in email_threads:
    
    
    return extracted_info

# def categorize_email(email_data):
#     # Categorize emails based on certain conditions (can be modified)
#     if "INBOX" in email_data["labelIds"]:
#         if "UNREAD" in email_data["labelIds"]:
#             if re.search(r"(urgent|asap|important)", email_data["snippet"], re.I):
#                 return "fetch_response"
#             elif re.search(r"(follow up|reminder)", email_data["snippet"], re.I):
#                 return "write_followup"
#         else:
#             if email_data["from"]:
#                 return "categorize"
#     return "no_action"

#to use the data returned from process_email_data to extract relevant information for batch reply
def extract_req_details():
    # gmail_reply_message(service,sender,recepient,subject,content,message_id='<CAHF40Kjn0ADUbno-u6RdVkWyXRDbazniKMOGQZa=QnmEttuyRw@mail.gmail.com>',thread_id='1926f87dba7e4f0e'):
    array_to_parse = process_email_data()

    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    mail_batch = []
    counter = 0
    for thread_dict in array_to_parse:
        # for message in thread_dict['messages']:
        imp_keys_dict = {}
        imp_keys_dict['threadId'] = thread_dict['threadId']
        imp_keys_dict['master_email'] = re.search(email_regex, thread_dict['snippet']).group()
        imp_keys_dict['recepient'] = thread_dict['from']
        imp_keys_dict['labels'] = thread_dict['labelIds']
        imp_keys_dict['subject'] = thread_dict['subject']
        imp_keys_dict['message_id'] = thread_dict['message_id']
        imp_keys_dict['conversation'] = thread_dict['conversation']
        imp_keys_dict['entry_no'] = counter + 1
        counter = counter + 1
        mail_batch.append(imp_keys_dict)

    
    return mail_batch

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
        
        # Convert matches into the desired dictionary format
        responses = {number: body.strip() for number, body in matches}
        
        return responses

#to respond to unread mails in the thread after generating responses from LLM
def batch_reply():

    # req_details = extract_req_details()
    req_details = show_chatty_threads_2()
    response_parameters = [{'subject' : entry['subject'], 'conversation':entry['conversation']} for entry in req_details]
    follow_up_messages = generate_batch_response_for_bulk_reply(response_parameters)

    response = extract_emails_regex(follow_up_messages)
    print(response)
    for idx, entry in enumerate(req_details,start = 1):
    # gmail_reply_message(sender,recepient,subject,content,message_id,thread_id):
        idx = str(idx)
        gmail_reply_message(entry['master_email'],entry['recepient'],entry['subject'],response[idx],entry['message_id'],entry['threadId'])
    
    print("successfully sent")

#to genenrate follow up messages for a batch of emails for replying in bulk
def generate_batch_response_for_bulk_reply(response_parameters):
    print(response_parameters[0]['subject'])
    print(response_parameters[0]['conversation'])
    print()
    batch = get_batches(response_parameters)
    print(batch)
    print()
    buffer = generate_response(batch)
    f = open("demofile4.txt", "w")
    f.write(buffer)
    f.close()
    print("done")
    return buffer

def decode_base64(s):
    decoded_msg = base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))
    utf_msg = decoded_msg.decode('utf-8')
    return utf_msg

def show_chatty_threads_2():
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

        # pylint: disable=maybe-no-member
        # pylint: disable:R1710
        threads = (
            service.users().threads().list(userId="me", q="is:unread").execute().get("threads", [])
        )
        lengthy_threads = []
        print(len(threads))

        for thread in threads:
            tdata = (
                service.users().threads().get(userId="me", id=thread["id"]).execute()
            )
            nmsgs = len(tdata["messages"])
            print(nmsgs)
            conversation = []
            thread['threadId'] = thread["id"]

            if nmsgs >= 3:
                messages = tdata['messages']
                
                for mssg in messages:

                    if 'labelIds' in mssg and 'UNREAD' in mssg['labelIds']:
                        thread['in_reply_to'] = mssg['id']

                    if 'labelIds' in mssg and 'TRASH' in mssg['labelIds']:
                        threads.remove(thread)
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
                thread['conversation'] = conversation
                lengthy_threads.append(thread)
                # return lengthy_threads
            
            
        return lengthy_threads

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    # print(show_chatty_threads_2())
    print(batch_reply())
#    f = open("demofile3.txt", "w")
#    f.write(str(process_email_data()))
#    f.close()
    # emails = show_chatty_threads()[1]

    # Prepare a dictionary to hold messages by thread ID
    # threads_dict = {}

    # for email in emails:
    #     thread_id = email.get("threadId")
        
    #     # If the thread ID is not already in the dictionary, initialize it
    #     if thread_id not in threads_dict:
    #         threads_dict[thread_id] = []

    #     conversation = []
    #     parts = email.get("messages").get("parts")
    #     for part in parts:
    #         s = part.get("body").get("data")
    #         decoded_msg = base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))
    #         if(part.get("mimeType")=="text/plain"):
    #             msg = decoded_msg.decode('utf-8')
    #             conversation.append(msg)
    #     print(conversation)
    #     print(len(conversation))
    # for thread in process_email_data():
    #     for message in thread:
    #         print(message['conversation'][0])
    #         print('---------------------------------')
    #     print('========================================')
