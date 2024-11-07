""""module for email automation logic"""
from flask import Flask, request, jsonify #pylint: disable=unused-import
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/emails_api', methods=['GET'])
@app.route('/')
def leads_api():
    """template route handler"""
    return jsonify({"status":
        "UNDER CONSTRUCTION"
    })

if __name__ == '__main__':
    app.run(debug=True,port=8000)
