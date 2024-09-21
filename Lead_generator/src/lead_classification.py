# src/lead_classification.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

from mongodb_integration import fetch_leads
from model import predict_lead

import tensorflow as tf

# Suppress most messages:
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def classify_lead(job_title, industry):
    """
    Classify the lead type based on job title and industry.
    """
    lead_type = predict_lead(job_title, industry)
    return lead_type


def lead_classification_update():
    leads = fetch_leads()
    for i in range(len(leads)):
        job_title = leads[i]['Job Title']
        industry = leads[i]['Industry']
        lead_type = classify_lead(job_title,industry)
        leads[i]['lead_type'] = lead_type
    return leads


# # Example usage
# if __name__ == "__main__":
#     job_title = "president"
#     industry = "medical device"
#     lead_type = classify_lead(job_title, industry)
#     print(f"The lead type for '{job_title}' in '{industry}' is '{lead_type}'.")
