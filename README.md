# Pharmacist Assistant

A simple AI pharmacy assistant built with Streamlit and OpenAI. It helps people check medication stock, get usage information, and verify prescriptions.

## What it does

The assistant can help with:
- Checking if medications are in stock
- Getting medication information and usage instructions
- Verifying prescription status
- Looking up your prescriptions

## How it works

Basically, you talk to it through a web interface, and it uses GPT-4 to understand what you need. Then it calls some tools to look up information from a database (stored as JSON files). The whole thing is stateless - it remembers your conversation during a session but forgets everything when you close it.

The main pieces are:
- **Streamlit app** (`app/main.py`) - the web interface
- **Agent** (`app/agent/agent.py`) - handles the conversation with OpenAI
- **Tools** (`app/agent/tools/actions.py`) - the actual functions that look things up
- **Database** (`app/database/`) - JSON files with user and medication data
- **Flows** (`app/agent/flows.py`) - defines how the agent should handle different types of requests

I implemented a decorator-based tool system where you just annotate functions with `@tool`, and it automatically generates the OpenAI function schemas from the function signatures and docstrings. This keeps the code DRY - the function definition is the single source of truth, so there's no risk of the schema getting out of sync with the implementation.

## Getting started

1. Clone the repo and install dependencies:
```bash
git clone `https://github.com/shoamafeka/PharmacistAssistant.git`
cd PharmacistAssistant
pip install -r requirements.txt
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your-key-here
```

3. Use Docker:
```bash
docker build -t pharmacist-assistant .
docker run -p 3000:3000 --env-file .env pharmacist-assistant
```

Then open `http://localhost:3000` in your browser.

## The tools

There are four main tools the agent can use:

1. **get_user_prescriptions(user_id)** - Gets all prescriptions for a user
2. **get_medication_info(medication_name)** - Looks up medication details (supports fuzzy matching)
3. **check_medication_stock(medication_names)** - Checks if medications are in stock
4. **verify_prescription(user_id, prescription_id)** - Verifies a prescription's status

## The data

The app comes with some sample data:
- `app/database/data/users.json` - 10 fake users with prescriptions
- `app/database/data/medications.json` - 5 medications with details and stock info

## How the agent handles requests

The agent follows three main patterns:

**Stock Check**: You ask about availability → agent asks for medication name → checks stock → tells you if it's in stock, low stock, or out of stock.

**Usage Info**: You ask how to use something → agent asks for medication name → looks up info → gives you usage instructions.

**Prescription Verification**: You want to verify a prescription → agent asks for your ID and prescription ID → verifies it → checks medication info and stock → gives you the full status.

## Testing

There's a testing guide in `evaluation/evaluation.md` with scenarios for testing all the flows.




