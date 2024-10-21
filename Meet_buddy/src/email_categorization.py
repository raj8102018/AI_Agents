from transformers import pipeline

# we are using 'distilbert-base-uncased-finetuned-sst-2-english' model for sentiment-analysis. Instead of explicitly importing it we use pipeline API to load the model when we use the argument below.

sentiment_analyzer = pipeline("sentiment-analysis")

#for explicitly mentioning the name of the model in the code we can use
#sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Function to analyze email and categorize based on sentiment
def categorize_email_sentiment(email_text):
    # Perform sentiment analysis
    sentiment = sentiment_analyzer(email_text)[0]
    label = sentiment['label']
    score = sentiment['score']

    # Categorize based on label and score
    if label == "POSITIVE":
        if score > 0.90:
            return "great prospect"  # Highly positive sentiment
        elif score > 0.70:
            return "decent"
        else:
            return "neutral"  # Mildly positive
    elif label == "NEGATIVE":
        if score > 0.90:
            return "ignore"  # Strongly negative sentiment, discard
        else:
            return "lower"  # Weak negative sentiment, but might still follow up
    else:
        return "neutral"  # Default case

# Example usage
email_content = "I really liked the offer, I would love to take the premium"
category = categorize_email_sentiment(email_content)
print(f"Email categorized as: {category}")
