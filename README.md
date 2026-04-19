# Smart Digital Finance Tracker

A CrewAI-powered personal finance dashboard with a 3-agent pipeline:
**Analyse → Advise → Report**

## Stack
- **Frontend**: Streamlit
- **Backend**: FastAPI + CrewAI
- **Database**: SQLite (memory.db)
- **CI/CD**: Jenkins + Docker
- **Deployment**: Streamlit Cloud

## Agents
| Agent | Role |
|-------|------|
| Expense Analyst | Analyses spending patterns from data |
| Financial Advisor | Provides actionable budgeting advice |
| Report Writer | Produces professional financial reports |

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API keys in .env
# OPENAI_API_KEY=...
# SERPER_API_KEY=...

# 4. Run the dashboard
streamlit run app/streamlit_app.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /analyse | Run AI finance analysis |
| POST | /transaction | Add a transaction |
| GET | /transactions | List all transactions |
| GET | /spending | Spending by category |

## Docker + Jenkins

```bash
# Start Jenkins + app
docker compose up -d

# Stop
docker compose down
```

## Deployment

Deploy to Streamlit Cloud:
1. Push repo to GitHub
2. Go to share.streamlit.io
3. Connect repo, set `app/streamlit_app.py` as main file
4. Add secrets (OPENAI_API_KEY, SERPER_API_KEY)
