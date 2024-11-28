"""
This module contains the functionality related to gmail api integration
"""

# pylint: disable=no-member
# pylint: disable=import-error
import sys
import os
import base64
import re
import time
import json
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .langchain_integration import (
    parallel_chain,
    get_query_answer,
    group_summaries_and_answers,
    postquery_refinement_chain,
)
from .email_response_generation import get_batches, get_summary, generate_response


# Add the parent directory to the Python path to access 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from Database.mongodb_connector import (
    leads_for_initial_contact,
    update_leads,
    connect_to_mongodb,
)


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
]
# SCOPES = ["https://mail.google.com/"]


def authenticate_gmail_api():
    """To authenticate with the gmail api. might open a window for consent during the first run"""
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
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def gmail_send_message(sender, recepient, subject, content):
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
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")


def gmail_reply_message(details):
    """reply to an email message and print the returned message ID."""
    try:
        service = authenticate_gmail_api()
        message = EmailMessage()
        content = details["content"].replace("\\n", "\n").replace("\n", "\n")
        message.set_content(content)
        message["To"] = details["recepient"]  # Recipient's email
        message["From"] = details["master_email"]  # Your email
        message["Subject"] = f"Re: {details["subject"]}"  # Use 'Re:' for replies

        # Set the In-Reply-To header
        message["In-Reply-To"] = details["message_id"]

        # Optional: Set References header (may help with threading)
        message["References"] = message["In-Reply-To"]

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            "raw": encoded_message,
            "threadId": details["threadId"],
        }  # Thread ID

        # Send the email
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")


def batch_mail_initiation(batch_size=1):
    """To initiate converstation in batch using the outbound messages stored in MongoDB"""
    authenticate_gmail_api()
    leads_collection = connect_to_mongodb()
    leads_data_tuple = leads_for_initial_contact(leads_collection)
    leads_to_contact = leads_data_tuple[0]
    sender = "yuvraj07102024@gmail.com"

    for i in range(0, len(leads_to_contact), batch_size):
        batch = leads_to_contact[i : i + batch_size]
        # gmail_send_message(sender,recepient,subject,content):
        for entry in batch:
            gmail_send_message(
                sender, entry["recepient"], entry["subject"], entry["content"]
            )
            print("sent..." + str(len(batch)))
        time.sleep(5)
    print("Changing contact status")
    update_leads(leads_data_tuple[1], leads_collection)
    print("successfully sent")


def extract_emails_regex(content):
    """To use regular expressions to match "Email n" followed by the email body"""
    email_pattern = r"\*\*Email\s(\d+):\*\*(.*?)(?=\*\*Email|\Z)"

    # Find all matches with the pattern
    matches = re.findall(email_pattern, content, re.DOTALL)
    print(matches)
    # Convert matches into the desired dictionary format
    responses = {int(number): body.strip() for number, body in matches}

    return responses


def generate_batch_response_for_bulk_reply(response_parameters):
    """To genenrate follow up messages for a batch of emails for replying in bulk"""
    batch = get_batches(response_parameters)

    summaries = get_summary(batch)

    cleaned_summaries = re.sub(r"```json|```", "", summaries).strip()

    data_dict = json.loads(cleaned_summaries)

    print(data_dict)

    follow_up = generate_response(data_dict)

    return follow_up


def decode_base64(s):
    """Function for decoding the encoded message"""
    decoded_msg = base64.urlsafe_b64decode(s + "=" * (4 - len(s) % 4))
    utf_msg = decoded_msg.decode("utf-8")
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
            service.users()
            .threads()
            .list(userId="me", q="is:unread")
            .execute()
            .get("threads", [])
        )
        lengthy_threads = []

        for thread in threads:
            tdata = (
                service.users().threads().get(userId="me", id=thread["id"]).execute()
            )
            nmsgs = len(tdata["messages"])
            conversation = []
            only_received_msgs = []
            thread["threadId"] = thread["id"]
            is_last_msg_sent = False

            if nmsgs >= 2:
                messages = tdata["messages"]

                for mssg in messages:

                    if "labelIds" in mssg and "UNREAD" in mssg["labelIds"]:
                        thread["in_reply_to"] = mssg["id"]

                    if "labelIds" in mssg and "SENT" in mssg["labelIds"]:
                        is_last_msg_sent = True
                    elif "labelIds" in mssg and "SENT" not in mssg["labelIds"]:
                        is_last_msg_sent = False

                    if "labelIds" in mssg and "TRASH" in mssg["labelIds"]:
                        # threads.remove(thread)
                        continue

                    for header in mssg["payload"]["headers"]:
                        if header["name"] == "Subject":
                            if not header["value"].startswith("Re: "):
                                thread["subject"] = header["value"]
                        elif header["name"] == "Return-Path":
                            reply_to_email = header["value"]
                            if reply_to_email.startswith("<"):
                                reply_to_email = reply_to_email[1:]
                            if reply_to_email.endswith(">"):
                                reply_to_email = reply_to_email[:-1]
                            thread["recepient"] = reply_to_email
                            # thread["convo"] = msg
                        elif header["name"] == "To":
                            thread["master_email"] = header["value"]
                        elif header["name"].lower() == "date":
                            thread["date"] = header["value"]
                        elif header["name"].lower() == "message-id":
                            thread["message_id"] = header["value"]
                        elif header["name"].lower() == "in-reply-to":
                            thread["in_reply_to"] = header["value"]
                        elif header["name"].lower() == "references":
                            thread["references"] = header["value"]

                    body = mssg["payload"]["body"]
                    if body["size"] != 0:
                        conversation.append(decode_base64(body["data"]))
                    else:
                        parts = mssg["payload"]["parts"]
                        for part in parts:
                            if part["mimeType"] == "text/plain":
                                conversation.append(decode_base64(part["body"]["data"]))
                                only_received_msgs.append(conversation[-1])
                thread["conversation"] = conversation
                thread["only_received_msgs"] = only_received_msgs

                if not is_last_msg_sent:
                    lengthy_threads.append(thread)
                # return lengthy_threads

        return lengthy_threads

    except HttpError as error:
        print(f"An error occurred: {error}")


def find_key_in_dict(data, target_key):
    """
    Recursively searches for a specific key in a dictionary or nested dictionaries.
    """
    if not isinstance(data, dict):
        return None

    # Check if the key exists at the current level
    if target_key in data:
        return data[target_key]

    # Recursively search in nested dictionaries
    for key, value in data.items():
        if isinstance(value, dict):
            result = find_key_in_dict(value, target_key)
            if result is not None:
                return result

def clean_and_parse_json(json_string):
    """function for cleaning and parsing json string with delimiters"""
    try:
        cleaned = re.sub(r"```json|```", "", json_string).strip()
        return json.loads(cleaned)
    except ValueError:
        return None

def batch_reply():
    """To respond to the unread emails in batches"""
    post_data = {"addLabelIds": [], "removeLabelIds": ["UNREAD"]}
    req_details = show_chatty_threads()
    if len(req_details) > 0:
        response_parameters = [
            {
                "subject": entry["subject"],
                "conversation": entry["conversation"],
                "date": entry["date"],
            }
            for entry in req_details
        ]
        batch = get_batches(response_parameters)

        first_data_input = {
            "input": json.dumps(batch)
        }  # Changed "first_entries" to "input"
        # print(first_data_input)
        final_output = parallel_chain.invoke(first_data_input)
        # cleaned_summaries = re.sub(r"```json|```", "", summaries).strip()
        first_final_output = None
        if isinstance(final_output, dict):
            first_final_output = final_output.get("first_thread")
        elif isinstance(final_output, str):
            try:
                first_final_output = json.loads(final_output).get("first_thread")
            except ValueError:
                print("Error parsing final_output as JSON.")
        print(f"first_final_output : {first_final_output}")
        print(f"first_final_output_type : {type(first_final_output)}")
        if isinstance(first_final_output, dict):
            first_final_output = first_final_output.get("followup_suggested")
        elif isinstance(first_final_output, str):
            first_final_output = clean_and_parse_json(first_final_output)
            if isinstance(first_final_output, str):
                first_final_output = json.loads(first_final_output)
        print(type(first_final_output))
        print(first_final_output)
        print(final_output["second_thread"])
        required_dict = final_output["second_thread"]
        required_dict = json.loads(required_dict)
        required_questions = str(required_dict["questions"])
        output = get_query_answer.invoke(required_questions)
        print(output)
        print(type(output))
        required_dict["answers"] = find_key_in_dict(output,'output_text')
        del required_dict["questions"]
        grouped_output = group_summaries_and_answers(required_dict)
        output_dict = postquery_refinement_chain.run({"entries": grouped_output})
        final_output_dict = json.loads(output_dict)
        print("\n\n\n\n\n")
        print(f"final_output_dict - {final_output_dict}")
        print(type(final_output_dict))
        print(f"final output dict: {final_output_dict["Follow up Suggested"]}")

        follow_up_details = (
            first_final_output["followup_suggested"]
            | final_output_dict["Follow up Suggested"]
        )
        scheduled_meet_details = (
            first_final_output["meeting_scheduled"]
            | final_output_dict["Meeting Scheduled"]
        )
        recontact_needed_details = (
            first_final_output["recontact_needed"]
            | final_output_dict["Recontact Needed"]
        )
        print(follow_up_details)
        follow_up_details_arr = [
            scheduled_meet_details,
            recontact_needed_details,
            follow_up_details,
        ]

        service = authenticate_gmail_api()
        for idx, entry in enumerate(req_details, start=1):
            if str(idx) in follow_up_details_arr[2].keys():
                # gmail_reply_message(sender,recepient,subject,content,message_id,thread_id):
                details = {
                    "master_email": entry["master_email"],
                    "recepient": entry["recepient"],
                    "subject": entry["subject"],
                    "content": follow_up_details_arr[2][str(idx)],
                    "message_id": entry["message_id"],
                    "threadId": entry["threadId"],
                }
                gmail_reply_message(details)
                service.users().threads().modify(
                    userId="me", id=entry["threadId"], body=post_data
                ).execute()
            elif str(idx) in follow_up_details_arr[0] or follow_up_details_arr[1]:
                service.users().threads().modify(
                    userId="me", id=entry["threadId"], body=post_data
                ).execute()
        print("success")
