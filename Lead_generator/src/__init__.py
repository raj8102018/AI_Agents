# __init__.py

# Define the package version (optional)
__version__ = '0.1.0'

# Import core modules or functions for convenience
# Example of importing frequently used functions or classes for easy access
from .data_preprocessing import preprocess_data
from .model import train_model, evaluate_model
from .api_integration import fetch_data_from_api
from .lead_classification import classify_lead, generate_outreach_response


# Additional initialization logic (if any)
print("Lead Generator package initialized")

# Optionally, include an overview or description
def package_description():
    return "Lead Generator Package: Includes data preprocessing, model training, API integration, and lead classification."
