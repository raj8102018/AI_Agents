"""This module contains the functionality to categorize the lead using sentiment analysis"""
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from transformers import pipeline #pylint: disable=wrong-import-position

# we are using 'distilbert-base-uncased-finetuned-sst-2-english' model for sentiment-analysis.
# Instead of explicitly importing it
# we use pipeline API to load the model through the argument below.

sentiment_analyzer = pipeline("sentiment-analysis")

# for explicitly mentioning the name of the model in the code we can use
# sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english") #pylint: disable=line-too-long


# Function to analyze email and categorize based on sentiment
def categorize_email_sentiment(email_text):
    """This function categorizes the email received"""
    # Perform sentiment analysis
    sentiment = sentiment_analyzer(email_text)[0]
    label = sentiment["label"]
    score = sentiment["score"]

    # Categorize based on label and score
    if label == "POSITIVE":
        if score > 0.90:
            return "great prospect"  # Highly positive sentiment
        if score > 0.70:
            return "decent"
        return "neutral"  # Mildly positive
    if label == "NEGATIVE":
        if score > 0.90:
            return "ignore"  # Strongly negative sentiment, discard
        return "lower"  # Weak negative sentiment, but might still follow up
    return "neutral"  # Default case


# Example usage
EMAIL_CONTENT = "I really liked the offer, I would love to take the premium"
category = categorize_email_sentiment(EMAIL_CONTENT) #pylint: disable=invalid-name
print(f"Email categorized as: {category}")
