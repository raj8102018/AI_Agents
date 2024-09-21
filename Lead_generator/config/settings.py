# config/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB settings
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = 'lead_classifier_data'

# API Keys (if needed)
# LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY', 'your_default_api_key')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY','')
