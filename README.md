
# Agency Swarm - Automated AI Agents for Business Development

## Project Title and Description
**Project Name**: Agency Swarm - Automated AI Agents for Business Processes  
**Description**: A multi-agent AI framework designed to automate various aspects of businesses starting with business development, such as lead generation, lead classification, and email automation, to streamline sales and outreach processes.

## Table of Contents
- Project Overview
- Features
- Tech Stack
- Installation
- Configuration
- Usage
- Examples (optional)
- Contributing
- License

## Project Overview
**Purpose**: Automating repetitive tasks in business processes.  
**Objective**: reducing time, improving accuracy, reducing workforce and operating costs.  
**Architecture Summary**: Multiple agents work together in a swarm framework to achieve end to end tasks where there is minimum human intervention or complete automation is possible.

## Features
- **Lead Generation Agent**: Automatically fetches leads from Database and other sources, classifies leads as hot, warm, or cold based on specific criteria, creates outbound message for such leads and uploads them to the database.
- **Email Automation Agent**: Automates outbound emails by fetching them from database, manages follow-ups, and analyzes responses using NLP and sentiment analysis via API calls to GEMINI API or OPEN AI API, uses LangChain for proper integration.
- **Data Storage and Retrieval**: Uses MongoDB for real-time lead and email data storage and retrieval.
- **Dashboard**: A React front end to view metrics and control agent operations.
- **Automation**: Scheduled tasks and triggers for continuous, hands-free operation.

## Tech Stack
- **Languages and Frameworks**: Python, JavaScript (React), Flask
- **Libraries and APIs**:
    - **Machine Learning**: Transformers, Hugging Face
    - **Backend**: Flask
    - **Frontend**: React
    - **Database**: MongoDB
    - **APIs**: Gemini API, LinkedIn API, Gmail API, Google Calendar API
- **Other Tools**: LangChain for NLP operations

## Installation

## Configuration
Store API keys and environment variables in .env file

## Usage
Orchestrator.py manages all the agents acting as a coordinator. It can be used to run the system.

# Start Backend (Flask API)
python app.py

## Contributing
While there are AutoGen and CREW AI, etc frameworks, we are trying something different, focusing more on business processes rather than specific tasks. Any suggestions or contributions are welcome.

```
