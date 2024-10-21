from flask import Flask, jsonify, request
from flask_cors import CORS  # For enabling CORS
from mongodb_integration import create_user,get_user_by_email,get_user_by_username

# Initialize Flask app
app = Flask(__name__)
CORS(app)  

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
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    user_name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    pack = [first_name, last_name, user_name, email, password]

    if all(pack):
        if create_user(first_name, last_name, user_name, email, password):
            return jsonify({"message": "User created successfully!"}), 201
        else:
            return jsonify({"error": "User already exists!"}), 409  # Conflict status code
    return jsonify({"error": "missing parameters!"}), 400

# API Route for signing in (still incomplete)
@app.route('/sign_in', methods=['POST'])
def sign_in():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')

    if get_user_by_email(email) or get_user_by_username(username):
        # You would add your password check and response here
        return jsonify({"message": "User exists!"}), 200

    return jsonify({"error": "User does not exist!"}), 404

if __name__ == "__main__":
    app.run(debug=True)
