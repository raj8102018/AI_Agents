"""This module contains lead generator api routes and functionality"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# from model import predict_lead
import numpy as np
from transformers import BertTokenizer, TFBertForSequenceClassification

app = Flask(__name__)
CORS(app)


def load_model_and_tokenizer():
    "This function loads the trained model"
    model_dir = os.path.abspath("fine_tuned_bert")  # Use absolute path
    model = TFBertForSequenceClassification.from_pretrained(model_dir)
    tokenizer = BertTokenizer.from_pretrained(model_dir)
    return model, tokenizer


def predict_lead(job_title, industry):
    "This function takes the request parameters and makes predicitons"
    model, tokenizer = load_model_and_tokenizer()

    # Concatenate job title and industry
    text = f"{job_title} {industry}"
    tokens = tokenizer(
        text, padding=True, truncation=True, max_length=128, return_tensors="tf"
    )
    outputs = model(**tokens)
    logits = outputs.logits.numpy()
    predicted_class = np.argmax(logits, axis=1)[0]
    labels = {0: "cold", 1: "warm", 2: "hot"}

    return labels[predicted_class]


@app.route("/leads_api", methods=["GET"])
@app.route("/")
def leads_api():
    """This is the function defined for the route to get classification results"""
    # Get the title and industry from the URL query parameters
    title = request.args.get("title", type=str)
    industry = request.args.get("industry", type=str)

    # Check if both parameters are provided
    if not title or not industry:
        return (
            jsonify({"error": "Missing required parameters: 'title' or 'industry'"}),
            400,
        )

    # Call your lead classification function
    # lead_type = "very hot"
    lead_type = predict_lead(title, industry)

    # Return the result as a JSON response
    return jsonify({"title": title, "industry": industry, "lead_type": lead_type})


if __name__ == "__main__":
    app.run(debug=True)
