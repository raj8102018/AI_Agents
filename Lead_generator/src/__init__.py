"""This module contains logic for initializing the agent"""
# __init__.py
#pylint: disable=import-error

# Define the package version (optional)
__version__ = '0.1.0'

# Import core modules or functions for convenience
# Example of importing frequently used functions or classes for easy access
from .data_preprocessing import preprocess_data
from .lead_classification import classify_lead
from .mongodb_integration import fetch_leads


# Additional initialization logic (if any)
print("Lead Generator package initialized")

# Optionally, include an overview or description
def package_description():
    """prints a statement about package"""
    return "Lead Generator Package: Includes data preprocessing, model training, API integration, and lead classification."
