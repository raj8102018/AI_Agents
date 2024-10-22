from flask import Flask, jsonify, request, redirect, url_for, session
from flask_cors import CORS  # For enabling CORS
from mongodb_integration import create_user,get_user_by_email,get_user_by_username,verify_password
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

from dotenv import load_dotenv
load_dotenv()


# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key =  os.getenv('client-secret')

class Config:
    SECRET_KEY = 'your_secret_key'  # use a secure key for your app
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True 
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_email_password'

# API Route for creating a user
@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    user_name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Validate input fields
    if not all([first_name, last_name, user_name, email, password]):
        return jsonify({"error": "Missing parameters!"}), 400

    # Create user in the database
    if create_user(first_name, last_name, user_name, email, password):
        return jsonify({"message": "User created successfully!"}), 201
    else:
        return jsonify({"error": "User already exists!"}), 409


# API Route for signing in (still incomplete)
@app.route('/sign_in', methods=['POST'])
def sign_in():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    user_by_email = get_user_by_email(email)
    user_by_username = get_user_by_username(username)
    if user_by_email:
        if verify_password(user_by_email['password'], password):  # Check the stored password hash
            return jsonify({"message": "Sign-in successful!"}), 200
        else:
            return jsonify({"error": "Invalid password!"}), 401  # Incorrect password
    elif user_by_username:
        if verify_password(user_by_username['password'], password):  # Check the stored password hash
            return jsonify({"message": "Sign-in successful!"}), 200
        else:
            return jsonify({"error": "Invalid password!"}), 401  # Incorrect password
    else:
        return jsonify({"error": "User does not exist!"}), 404

if __name__ == "__main__":
    app.run(debug=True)
