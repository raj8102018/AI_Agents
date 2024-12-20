"""
This module contains the functionality related to different routes
"""
#pylint: disable=missing-timeout
#pylint: disable=import-error
import os, random, string
import sys
import json
import requests
import jwt
import pandas as pd
import os

from bson.objectid import ObjectId

from functools import wraps
from datetime import datetime, timezone, timedelta, UTC
from dotenv import load_dotenv
from flask import Flask, jsonify, request, redirect, url_for, session, render_template
from flask_cors import CORS  # For enabling CORS
from oauthlib.oauth2 import WebApplicationClient
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "src")))
# Add the parent directory to the Python path to access 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Config.settings import secretkey, clientid_auth, clientsecret_auth #pylint: disable=wrong-import-position
from Database.auth_database_connector import create_user, get_user_by_email, get_user_by_username, get_user_by_id, verify_password, create_guser # pylint: disable=line-too-long
from Database.lead_generator_connector import update_lead_with_form_data, create_leads, update_user_with_token
from Database.rag_connector import store_pdf_in_mongodb


from Email_automation.src.email_automation_agent import EmailAutomation
from Orchestrator.orchestrator import Orchestrator

email_automation_agent_instance = EmailAutomation()

load_dotenv()

# SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))
SECRET_KEY = 'FCUK'
mode = os.getenv('MODE')
domain_name = os.getenv('QSTATE_DOMAIN')
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
]

CLIENT_SECRETS_FILE = "credentials.json"
REDIRECT_URI = "https://localhost:5000/google_token/callback"

if mode=="PRODUCTION":
    REDIRECT_URI = domain_name+"/google_token/callback"

# Initialize Flask app
# app = Flask(
#     __name__,
#     static_url_path="/",
#     static_folder="/dist/assets",
#     template_folder="/dist",
# )
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__),  'dist'), static_folder=os.path.join(os.path.dirname(__file__), 'dist', 'assets'), static_url_path='/assets')

CORS(app)
app.secret_key = secretkey

# google Oauth configuration
GOOGLE_CLIENT_ID = clientid_auth
GOOGLE_CLIENT_SECRET = clientsecret_auth
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def token_required(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        token = None
        # print(token)

        if "authorization" in request.headers:
            token = request.headers["authorization"]
        # print(token)
        # data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # try:
        print("before decoding token")
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(data)
        expiry = data["expire_time"]
        print(expiry)
        format_date = "%Y-%m-%d %H:%M:%S.%f%z"
        expiry_date = datetime.strptime(expiry, format_date)
        if datetime.now(UTC) > expiry_date:
            print("token expired")
            # return redirect("https://localhost:3001/sign_in", code=302)
            return {"success": False, "msg": "Token Expired"}, 400
        else:
            print("token is valid and time left:")
            print(expiry_date - datetime.now(UTC))
            
        # except:
        #     return {"success": False, "msg": "Token is invalid"}, 400
        
        return func(*args, **kwargs)

    return decorator



def get_google_provider_cfg():
    """Function to get Google's provider configuration"""
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# Route to redirect the user to Google's OAuth page
@app.route("/glogin")
def login():
    """route handler to enable google login"""
    # Get Google's OAuth 2.0 provider configuration
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Create the request for Google login
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for("callback", _external=True),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


# Route to handle the callback from Google
@app.route("/glogin/callback")
def callback():
    """route handler to handle callback from google"""
    # Get the authorization code Google sent back to you
    code = request.args.get("code")

    # Get Google's token endpoint and exchange the code for tokens
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Extract user info (email, name, etc.)
    user_info = userinfo_response.json()

    # Check if user email is verified
    if user_info.get("email_verified"):
        email = user_info["email"]
        name = user_info["name"]

        # Create a user in your database using their email or check if they already exist
        user = get_user_by_email(email)  # Check if user exists in your database
        if not user:
            # If user doesn't exist, create the user
            user = create_guser(
                name, email
            )  # Define a create_user function to add the user to MongoDB

        # Log the user in (you can set session variables, etc.)
        
        
        token = jwt.encode({'email': user["email"], 'expire_time': str(datetime.now(UTC) + timedelta(minutes=300))}, SECRET_KEY)
        user["token"] = token
        session["user"] = email
        user["_id"] = str(user["_id"])
        return (
            jsonify(user),
            200,
        )
    return (
            jsonify({"error": "User email not available or not verified by Google"}),
            400,
        )


@app.route("/google_login", methods=['POST'])
def goodle_login():
    auth_code = request.get_json()['code']

    data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,  # client ID from the credential at google developer console
        'client_secret': GOOGLE_CLIENT_SECRET,  # client secret from the credential at google developer console
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
    headers = {
        'Authorization': f'Bearer {response["access_token"]}'
    }
    user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers).json()

    """
        check here if user exists in database, if not, add him
    """
    # print(user_info)
    # return jsonify(user_info)
    if user_info.get("email_verified"):
        email = user_info["email"]
        name = user_info["name"]

        # Create a user in your database using their email or check if they already exist
        user = get_user_by_email(email)  # Check if user exists in your database
        if not user:
            # If user doesn't exist, create the user
            user = create_guser(
                name, email
            )  # Define a create_user function to add the user to MongoDB

        # Log the user in (you can set session variables, etc.)
        
        
        token = jwt.encode({'email': user["email"], 'expire_time': str(datetime.now(UTC) + timedelta(minutes=30))}, SECRET_KEY)
        user["token"] = token
        session["user"] = email
        user["_id"] = str(user["_id"])
        print(user)
        return (
            jsonify(user),
            200,
        )

@app.route("/logout")
def logout():
    """route handler to enable logout"""
    session.clear()
    return redirect(url_for("index"))


# API Route for creating a user
@app.route("/esign_up", methods=["POST"])
def sign_up():
    """route handler for manual signup"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    first_name = data.get("firstname")
    last_name = data.get("lastname")
    user_name = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Validate input fields
    if not all([first_name, last_name, user_name, email, password]):
        return jsonify({"error": "Missing parameters!"}), 400

    # Create user in the database
    if create_user(first_name, last_name, user_name, email, password):
        return jsonify({"message": "User created successfully!"}), 201
    return jsonify({"error": "User already exists!"}), 409


@app.route("/", methods=['GET'])
def get_home():
    """default template route handler"""
    # return jsonify({"status": "UNDER CONSTRUCTION"})
    return render_template('index.html')


# API Route for signing in (still incomplete)
@app.route("/esign_in", methods=["POST"])
def sign_in():
    """route handler for manual signin"""
    data     = request.get_json()
    email    = data.get("email")
    username = data.get("username")
    password = data.get("password")

    print(username)
    print(data)

    user = {}
    if email == None:
        user = get_user_by_username(username)
    else:
        user = get_user_by_email(email)
    print("user down below")
    print(user)
    if not user:
        return jsonify({"error": "User does not exist!"}), 404
    if verify_password(user["password"], password):
        token = jwt.encode({'email': user["email"], 'expire_time': str(datetime.now(UTC) + timedelta(minutes=30))}, SECRET_KEY)
        user["message"] = "Sign-in successful!"
        session["token"]= token
        user["token"]= token
        user["_id"]     = str(user["_id"])
        # user["session"] = session
        # print(user)
        if 'token' in session:
            print('token in session found')
        else:
            print('token in session not found')
        print(user)
        return jsonify(user), 200
    return jsonify({"error": "User does not exist!"}), 404

    # if user_by_email:
    #     if verify_password(
    #         user_by_email["password"], password
    #     ):  # Check the stored password hash
    #         return jsonify({"message": "Sign-in successful!"}), 200
    #     return jsonify({"error": "Invalid password!"}), 401  # Incorrect password
    # if user_by_username:
    #     if verify_password(
    #         user_by_username["password"], password
    #     ):
            

    #         # Check the stored password hash
    #         return jsonify({
    #             "message": "Sign-in successful!!",
    #             "token"  : token
    #             }), 200
    #     return jsonify({"error": "Invalid password!"}), 401  # Incorrect password
    # return jsonify({"error": "User does not exist!"}), 404

# API Route for signing in (still incomplete)
# @token_required
@app.route("/profile/<user_id>", methods=["GET"])
@token_required
def get_user(user_id):
    """route handler for manual signin"""

    user = get_user_by_id(user_id)
    token = jwt.encode({'email': user["email"], 'expire_time': str(datetime.now(UTC) + timedelta(minutes=30))}, SECRET_KEY)
    user["message"] = "Sign-in successful!"
    session["token"]= token
    user["token"]= token
    user["_id"]     = str(user["_id"])
    return jsonify(user)

@app.route("/upload_files", methods=["POST"])
@token_required
def upload_files():
    try:
        # Check if files are in the request
        if not request.files:
            return jsonify({"error": "Missing file(s) in request"}), 400
        pdf_file = None
        excel_file = None
        
        for key, file in request.files.items():
            if file.filename.endswith('.pdf'):
                pdf_file = file
            elif file.filename.endswith(('.xls', '.xlsx', '.csv')):
                excel_file = file
        
        if not pdf_file or not excel_file:
            return jsonify({"error": "Missing required file(s). PDF and CSV are required."}), 400
         
        frequency = request.form.get('frequency')
        user_id = request.form.get('user_id')
        company_name = request.form.get('company_name')
        agent_name = request.form.get('agent_name')

        # Validate form fields
        if not frequency or not user_id or not company_name or not agent_name:
            return jsonify({"error": "Missing form data"}), 400

        # Save the uploaded files
        # pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        # excel_path = os.path.join(UPLOAD_FOLDER, excel_file.filename)
        # pdf_file.save(pdf_path)
        # excel_file.save(excel_path)

        # Simulate processing or saving other form data if needed
        # print(f"PDF saved at: {pdf_path}")
        # print(f"Excel saved at: {excel_path}")
        print(f"Frequency: {frequency}")
        print(f"User ID: {user_id}")
        print(f"company name: {company_name}")
        print(f"agent_name: {agent_name}")

        df = pd.read_csv(excel_file)
        print(df)

        leads_to_insert = []
        for index, row in df.iterrows():
            print(index)
            print(row)
            lead = {
                "Company": row["Company"],
                "First Name": row["First Name"],
                "Last Name": row["Last Name"],
                "Email": row["Email"],
                "Job Title": row["Profession"],
                "Website": row["Website"],
                "Address": row["Address"],
                "user_id": ObjectId(user_id),
                "Industry": row["Industry"],
                "Initial contact": "No"
            }
            leads_to_insert.append(lead)
        
        create_leads(leads_to_insert)
        

        update_lead_with_form_data(user_id,frequency,company_name,agent_name)
        store_pdf_in_mongodb(user_id,pdf_file)


        
        # Respond to the client
        return jsonify({
            "message": "Files uploaded successfully",
            # "pdf_path": pdf_path,
            # "excel_path": excel_path,
            "frequency": frequency,
            "user_id": user_id
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route("/execute/", methods=["POST"])
@token_required
def run_email_automation():
    user_id = request.form.get('user_id')
    company_name = request.form.get('company_name')
    orchestrator_instance = Orchestrator(user_id,company_name)
    orchestrator_instance.run()
    del orchestrator_instance

    # email_automation_agent_instance.run()
    # email_automation_agent_instance.initiate_email()
    return {"message": "Successfully Ran EA"}, 200

auth_flows = {}
state_to_user = {}

@app.route('/get-auth-url/<user_id>', methods=['GET'])
def get_auth_url(user_id):
    """Generate the authorization URL and return it to the frontend."""
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    
    # Save the flow instance for later use

    # Generate the authorization URL
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        user_id= user_id
    )

    auth_flows[state] = flow
    state_to_user[state] = user_id

    print(state)
    print("-----State^^^^")

    # Return the URL to the frontend
    return jsonify({'auth_url': auth_url})

@app.route('/google_token/callback', methods=['GET'])
def gtoken_callback():
    """Handle the OAuth callback."""
    state = request.args.get('state')  # Pass `state` to identify the user
    code = request.args.get('code') 

    # Retrieve the flow instance using state/user_id
    flow = auth_flows.pop(state, None)
    user_id = state_to_user.pop(state, None)

    if not flow:
        return jsonify({'error': 'Invalid state or user ID'}), 400

    flow.fetch_token(code=code)

    # Save credentials
    creds = flow.credentials
    target_token = f"tokens/{user_id}_token.json"
    os.makedirs(os.path.dirname(target_token), exist_ok=True)
    with open(target_token, 'w', encoding='utf-8') as token_file:
        token_file.write(creds.to_json())

    update_result = update_user_with_token(user_id, creds)

    return jsonify({'message': 'Authentication successful, You can close this window.'})

if __name__ == "__main__":
    # app.run(debug=True)
    
    app.run(host='0.0.0.0', ssl_context=('example.com+5.pem', 'example.com+5-key.pem'), debug=True)
    # app.run(ssl_context="adhoc", debug=True)
