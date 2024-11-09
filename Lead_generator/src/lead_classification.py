"""
This module contains lead-classification logic
"""
# src/lead_classification.py
from model import predict_lead # pylint: disable=import-error


def lead_classification_update(leads):
    """
    Classify the lead type based on job title and industry
    """
    for lead in leads:
        job_title = lead['Job Title']
        industry = lead['Industry']
        lead_type = predict_lead(job_title, industry)  
        lead['lead_type'] = lead_type
    return leads


if __name__ == "__main__":
    pass
