from flask import Flask, request, jsonify
from model import predict_lead
import numpy as np
import os


app = Flask(__name__)

@app.route('/leads_api', methods=['GET'])
def leads_api():
    # Get the title and industry from the URL query parameters
    title = request.args.get('title', type=str)
    industry = request.args.get('industry', type=str)
    
    # Check if both parameters are provided
    if not title or not industry:
        return jsonify({"error": "Missing required parameters: 'title' or 'industry'"}), 400

    # Call your lead classification function
    lead_type = "very hot"
    lead_type = predict_lead(title, industry)

    # Return the result as a JSON response
    return jsonify({
        "title": title,
        "industry": industry,
        "lead_type": lead_type
    })

if __name__ == '__main__':
    print(predict_lead("President", "Retail"))
    app.run(debug=True)
