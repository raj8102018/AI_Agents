"""This module contaings api function logic for email automation"""
from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/emails_api', methods=['GET'])
@app.route('/')
def leads_api():
    """temporary place holder function"""
    return jsonify({
        "status":"UNDER CONSTRUCTION"
    })

if __name__ == '__main__':
    app.run(debug=True,port=8000)
