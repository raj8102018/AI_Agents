"""
This module contains the functionality related to different routes
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, redirect, url_for, session
from flask_cors import CORS  # For enabling CORS
from oauthlib.oauth2 import WebApplicationClient


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "src")))
# Add the parent directory to the Python path to access 'config'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Config.settings import (
    secretkey,
    clientid_auth,
    clientsecret_auth,
)  # pylint: disable=wrong-import-position
from Database.auth_database_connector import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    verify_password,
    create_guser,
)  # pylint: disable=line-too-long


load_dotenv()


# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = secretkey

# google Oauth configuration
GOOGLE_CLIENT_ID = clientid_auth
GOOGLE_CLIENT_SECRET = clientsecret_auth
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


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

        # You can now create a user in your database using their email or check if they already exist
        # For example:
        user = get_user_by_email(email)  # Check if user exists in your database
        if not user:
            # If user doesn't exist, create the user
            create_guser(
                name, email
            )  # Define a create_user function to add the user to MongoDB

        # Log the user in (you can set session variables, etc.)
        session["user"] = email

        return (
            jsonify({"message": "Login successful!", "email": email, "name": name}),
            200,
        )
    else:
        return (
            jsonify({"error": "User email not available or not verified by Google"}),
            400,
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
    else:
        return jsonify({"error": "User already exists!"}), 409


@app.route("/", methods=["GET"])
def get_home():
    """default template route handler"""
    return jsonify({"status": "UNDER CONSTRUCTION"})


# API Route for signing in (still incomplete)
@app.route("/esign_in", methods=["POST"])
def sign_in():
    """route handler for manual signin"""
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    print(username)

    user_by_email = get_user_by_email(email)
    user_by_username = get_user_by_username(username)
    if user_by_email:
        if verify_password(
            user_by_email["password"], password
        ):  # Check the stored password hash
            return jsonify({"message": "Sign-in successful!"}), 200
        else:
            return jsonify({"error": "Invalid password!"}), 401  # Incorrect password
    elif user_by_username:
        if verify_password(
            user_by_username["password"], password
        ):  # Check the stored password hash
            return jsonify({"message": "Sign-in successful!!"}), 200
        else:
            return jsonify({"error": "Invalid password!"}), 401  # Incorrect password
    else:
        return jsonify({"error": "User does not exist!"}), 404


if __name__ == "__main__":
    app.run(ssl_context="adhoc", debug=True)
