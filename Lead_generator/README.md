# Lead Generation AI Agent

## Overview
This project focuses on developing AI agent that can identify and classify leads, automatically draft personalized outreach responses and a few other tasks.

## Possible swarm role

Feed relevant leads into other agents for tasks like follow-up etc

# to temporarily change the execution policy to allow the script to run.

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

To activate the environment use the command below

.\my_env\Scripts\Activate.ps1


<!-- Lead_generator/
│
├── data/
│   ├── raw/
│   │   └── leads_dataset.csv
│   └── processed/
│       └── cleaned_leads.csv
│
├── notebooks/
│   └── lead_generation_exploration.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py        # Modified to include dataset export functionality
│   ├── model.py                     # Handles model training and prediction logic
│   ├── api_integration.py           # Integrates with LinkedIn or other APIs
│   ├── lead_classification.py       # Lead classification logic (calls prediction function)
│   ├── mongodb_integration.py       # Handles MongoDB data retrieval and storage
│   ├── response_generation.py       # Drafts personalized outreach responses
│   └── utils.py                     # Utility functions (logging, common helper functions)
│
├── tests/
│   └── test_data_preprocessing.py
│   └── test_model.py
│   └── test_mongodb_integration.py  # Tests for MongoDB integration (new)
│   └── test_response_generation.py  # Tests for automated response generation (new)
│
├── requirements.txt
├── README.md
├── .gitignore
├── config/
│   └── settings.py                  # Configuration for API keys, MongoDB settings, etc.
│
└── my_env/ -->


# Errors and resolution when you pip install
nlp         = spacy.load('en_core_web_sm')
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              cannot find module

Resolution  = python -m spacy download en || python -m spacy download en_core_web_sm

