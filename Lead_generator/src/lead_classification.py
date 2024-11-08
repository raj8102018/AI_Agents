"""
This module contains lead-classification logic
"""
# src/lead_classification.py
#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
import sys
import os
from .model import predict_lead # pylint: disable=import-error

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Database.lead_generator_connector import fetch_leads #pylint: disable=import-error

def classify_lead(job_title, industry):
    """
    classification logic.
    """
    lead_type = predict_lead(job_title, industry)
    return lead_type


def lead_classification_update():
    """
    Classify the lead type based on job title and industry
    """
    leads = fetch_leads()
    for lead in leads:
        job_title = lead['Job Title']
        industry = lead['Industry']
        lead_type = classify_lead(job_title, industry)
        lead['lead_type'] = lead_type
    return leads

if __name__ == "__main__":
    pass
