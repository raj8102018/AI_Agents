"""
This module contains lead-classification logic
"""
# src/lead_classification.py
import sys
import os
from mongodb_integration import fetch_leads # pylint: disable=import-error
from model import predict_lead # pylint: disable=import-error

# import tensorflow as tf

# # Suppress most messages:
# tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

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
