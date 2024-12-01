"""
This module contains the configuration details for meet_buddy
"""
# config/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB settings
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = 'test_emails_responses'

# API Keys (if needed)
# LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY', 'your_default_api_key')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY','')
