from flask import Flask, jsonify, request
from flask_cors import CORS  # For enabling CORS
from mongodb_integration import connect_to_mongodb,create_user,get_user_by_email,verify_password

# Initialize Flask app
app = Flask(__name__)
CORS(app)  

# API Route for creating a user
@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    user_name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    pack = [first_name,last_name,user_name,email,password]

    if all(pack):
        if create_user(first_name,last_name,user_name,email, password):
            return jsonify({"message": "User created successfully!"}), 201
        else:
            return jsonify({"error": "User already exists!"}), 409  # Conflict status code
    return jsonify({"error": "missing parameters!"}), 400

@app.route('/sign_in')
def sign_in():
    data = request.get_json()
    email = data.get('email')
    
if __name__ == "__main__":
    app.run(debug=True)