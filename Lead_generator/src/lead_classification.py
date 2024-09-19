# src/lead_classification.py
from model import predict_lead

def classify_lead(job_title, industry):
    """
    Classify the lead type based on job title and industry.
    """
    lead_type = predict_lead(job_title, industry)
    return lead_type

# Example usage
if __name__ == "__main__":
    job_title = "president"
    industry = "medical device"
    lead_type = classify_lead(job_title, industry)
    print(f"The lead type for '{job_title}' in '{industry}' is '{lead_type}'.")
