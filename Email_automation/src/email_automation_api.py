from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import os


app = Flask(__name__)
CORS(app)

@app.route('/emails_api', methods=['GET'])
def leads_api():
        return jsonify({"status":
        "UNDER CONSTRUCTION"
    })

if __name__ == '__main__':
    app.run(debug=True,port=8000)
