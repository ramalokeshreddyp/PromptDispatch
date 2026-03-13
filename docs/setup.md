# Setup Guide

Quick steps to get Prompt Router running locally or with Docker.

## Prerequisites

- Python 3.11+ (or Docker)
- An OpenAI API key

## Local Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd Prompt-Router

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
copy .env.example .env
# Edit .env and paste your OPENAI_API_KEY

# 5. Run the server
uvicorn app.main:app --reload
```

Open **http://localhost:8000** in your browser.

## Docker Setup

```bash
# 1. Create your .env
copy .env.example .env
# Edit .env and paste your OPENAI_API_KEY

# 2. Build and run
docker compose up --build
```

Open **http://localhost:8000** in your browser.

## Environment Variables

| Variable              | Required | Default          | Description                     |
|-----------------------|----------|------------------|---------------------------------|
| `OPENAI_API_KEY`      | Yes      | —                | Your OpenAI API key             |
| `CLASSIFIER_MODEL`    | No       | `gpt-4o-mini`   | Model for intent classification |
| `GENERATOR_MODEL`     | No       | `gpt-4o-mini`   | Model for response generation   |
| `CONFIDENCE_THRESHOLD`| No       | `0.7`            | Below this → treated as unclear |
| `LOG_FILE`            | No       | `route_log.jsonl`| Path to the log file            |
