# 💰 Digital Smart Finance Tracker v5

> **Quartet Protocol — Mission Charlie: Analyst + Reporting Engine.**  
> A real-time stock & crypto dashboard · 3-agent AI financial analysis · loan rate tracker · time-value-of-money calculator — all in one Streamlit app, containerised with Docker and shipped via a Jenkins CI/CD pipeline.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red?logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![CrewAI](https://img.shields.io/badge/CrewAI-multi--agent-orange)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20Anthropic-purple)
![Jenkins](https://img.shields.io/badge/CI%2FCD-Jenkins-D24939?logo=jenkins)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 What Is This App?

The **Digital Smart Finance Tracker v5** is a full-stack personal finance and investment platform. It pulls live market data for any stock or cryptocurrency, renders interactive candlestick charts, runs a silent 3-agent AI crew to analyse your finances, tracks major loan interest rates, and includes a full time-value-of-money calculator.

No finance jargon. No technical setup for end users. Just enter a ticker or question and get answers.

---

## 📸 App Tabs at a Glance

| Tab | What It Does |
|-----|-------------|
| 📈 **Markets** | Live candlestick chart, volume, MA20/MA50, key metrics for any stock or crypto |
| 🤖 **AI Analysis** | Ask any finance question — get a structured professional report in 1–3 minutes |
| 📊 **My Finances** | Major loan rates (daily/weekly/monthly) + spending pie chart + transaction history |
| ➕ **Add Transaction** | Log daily expenses with date, amount, category, and description |
| 🧮 **Calculator** | Simple & compound interest, FV, PV, FV Annuity, PV Annuity — with growth charts |

---

## 🏗️ Project Structure

```
digital-smart-finance-tracker-v5/
│
├── app/
│   ├── streamlit_app.py        # Main dashboard — 5 tabs, charts, AI analysis UI
│   └── main.py                 # FastAPI backend (5 REST endpoints)
│
├── src/
│   ├── crew.py                 # AI orchestration — 3-agent A-A-R pipeline
│   ├── agents/
│   │   └── __init__.py
│   ├── tasks/
│   │   └── __init__.py
│   └── tools/
│       ├── calculators.py      # Time-value-of-money formulas (6 functions)
│       ├── custom_tools.py     # SQL guardrail, web scraper, context writer
│       ├── database.py         # SQLite — transactions, budgets, run history
│       ├── debug_tools.py      # Execution tracer & smoke test
│       └── resilience.py       # 4-layer resilience stack (retry, budget, schema, reviewer)
│
├── config/
│   ├── agents.yaml             # Agent role / goal / backstory definitions
│   └── tasks.yaml              # Task descriptions and expected outputs
│
├── tests/
│   ├── test_calculators.py     # Unit tests for all TVM formulas
│   └── test_basic.py           # Basic smoke tests
│
├── jenkins/
│   └── create-pipeline-job.groovy   # Script to auto-create the Jenkins job
│
├── .devcontainer/
│   └── devcontainer.json       # VS Code Dev Container config
│
├── .streamlit/
│   └── secrets.toml.example    # Secrets template for Streamlit Cloud
│
├── .env.example                # Environment variables template
├── .gitignore
├── Dockerfile                  # Python 3.12-slim image, port 8501
├── docker-compose.yml          # Jenkins (8080) + App (8501)
├── Jenkinsfile                 # 4-stage ADLC CI/CD pipeline
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Option A — Docker (recommended, zero setup)

```bash
git clone https://github.com/aftonis/digital-smart-finance-tracker-v5.git
cd digital-smart-finance-tracker-v5

# Copy the env template and add your keys
cp .env.example .env
# Edit .env — see "Environment Variables" section below

# Start the app
docker compose up -d app

# Open in browser
# → http://localhost:8501
```

### Option B — Run locally without Docker

```bash
git clone https://github.com/aftonis/digital-smart-finance-tracker-v5.git
cd digital-smart-finance-tracker-v5

pip install -r requirements.txt

# Copy and edit secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your keys

streamlit run app/streamlit_app.py
# → http://localhost:8501
```

---

## 🔑 Environment Variables

The app supports **two free LLM providers** — pick one:

### Option 1: Groq (free, fast — recommended for getting started)

Create a free account at [console.groq.com](https://console.groq.com) → API Keys → Create.

```env
# .env
GROQ_API_KEY=gsk_your_groq_key_here
CLAUDE_MODEL=groq/llama-3.3-70b-versatile

# Optional — web search for the AI agents
# SERPER_API_KEY=your_serper_key_here
```

### Option 2: Anthropic Claude (pay-per-use)

```env
# .env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
CLAUDE_MODEL=anthropic/claude-3-5-haiku-latest

# Optional
# SERPER_API_KEY=your_serper_key_here
```

> ⚠️ **Never commit real keys.** `.env` and `.streamlit/secrets.toml` are gitignored — only the `.example` versions are pushed to GitHub.

See [`.env.example`](.env.example) and [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example) for full templates.

---

## ☁️ Deploy to Streamlit Cloud (free)

1. **Fork** or push this repo to your own GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select the repo, branch `main`, main file `app/streamlit_app.py`
4. Click **Advanced settings → Secrets** and paste:

   ```toml
   # Using Groq (free tier)
   GROQ_API_KEY = "gsk_your_groq_key_here"
   CLAUDE_MODEL = "groq/llama-3.3-70b-versatile"

   # Or using Anthropic
   # ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
   # CLAUDE_MODEL = "anthropic/claude-3-5-haiku-latest"
   ```

5. Click **Deploy** — your app goes live at `https://<name>.streamlit.app`

Every push to `main` triggers an automatic redeploy.

---

## 🤖 AI Analysis — 3-Agent Pipeline

Behind the scenes a silent AI crew analyses your query using three specialised agents working in sequence:

```
  User query
      │
      ▼
┌─────────────────┐      ┌──────────────────────┐      ┌───────────────────┐
│ Expense Analyst │ ───► │ Financial Advisor     │ ───► │  Report Writer    │
│                 │      │                       │      │                   │
│ • Queries DB    │      │ • 50/30/20 budgeting  │      │ • Structures into │
│ • Web research  │      │ • Zero-based budget   │      │   Overview →      │
│ • Spots trends  │      │ • Actionable advice   │      │   Findings →      │
│                 │      │                       │      │   Recommendations │
└─────────────────┘      └──────────────────────┘      └───────────────────┘
                                                                │
                                                                ▼
                                                     Downloadable .md report
```

Every report is structured as:
1. **Overview** — summary of the financial situation
2. **Key Findings** — data-grounded insights
3. **Recommendations** — prioritised action list
4. **Action Plan** — specific next steps

Agent definitions live in [`config/agents.yaml`](config/agents.yaml) · Task definitions in [`config/tasks.yaml`](config/tasks.yaml).

---

## 🛡️ Resilience Stack

The pipeline has 4 layers of fault protection:

| Layer | Protection | Detail |
|-------|-----------|--------|
| **L1 — Retry** | Exponential backoff + jitter | 3 retries; 429 rate-limit errors wait 65 s so the provider's token window resets |
| **L2 — Budget Cap** | `max_tokens=1500` per agent | Prevents runaway API costs; stays within Groq free-tier 6 k TPM limit |
| **L3 — Schema Enforcement** | Pydantic validation | All structured JSON outputs validated against `StructuredFinanceReport` |
| **L4 — Reviewer Agent** | Metacognition fact-check | Verifies report accuracy against source data before delivery |

---

## 🧮 Calculator — Time Value of Money

Six financial formulas, each with inputs, a result card, and a Plotly growth chart:

| Formula | Used For |
|---------|---------|
| Simple Interest `I = P·r·t` | Short-term loans, bonds |
| Compound Interest `A = P(1+r/n)^(n·t)` | Savings, deposits |
| Future Value | "What will my money be worth?" |
| Present Value | "What's a future payout worth today?" |
| FV Annuity | Retirement saving, SIPs |
| PV Annuity | Loan principal from regular repayments |

All compounding frequencies supported: annual, semi-annual, quarterly, monthly, weekly, daily.

---

## 📈 Markets — Real-Time Charts

Type any ticker and instantly get:

- **Candlestick chart** with volume bars — green for up, red for down
- **Moving averages** — MA20 and MA50 overlaid on price
- **Key metrics** — price, % change, market cap, 52-week high/low
- **Company summary** — expandable business overview
- **Configurable period & interval** — 1 month to 5 years, daily to monthly

Supported: stocks, ETFs, indices, cryptocurrencies:

```
AAPL  GOOGL  AMZN  TSLA  NVDA  MSFT
BTC-USD  ETH-USD  SOL-USD  BNB-USD
^GSPC (S&P 500)  ^DJI (Dow Jones)  ^IXIC (NASDAQ)
```

---

## 🏦 Loan Rate Tracker

Editable table of 9 major loan types (mortgage, auto, personal, credit card, student, HELOC, payday) with:

- Daily / Weekly / Monthly effective rate (APR ÷ 365 / 52 / 12)
- Daily / Weekly / Monthly / Yearly interest cost on your principal
- Grouped bar chart comparing cost across loan types

Edit any APR or principal → table and chart update instantly.

---

## 🔧 Jenkins CI/CD

The `Jenkinsfile` runs the full **4-stage ADLC pipeline** on every push to `main`:

| Stage | ADLC Phase | What It Does |
|-------|-----------|-------------|
| **Plan — Validate** | Phase 1 | Checkout, verify required files, scan for hard-coded secrets, check `.gitignore` |
| **Design — Test** | Phase 2 | Run `pytest tests/test_calculators.py` inside an isolated Docker container |
| **Execute — Docker Build** | Phase 3 | Build image, run container, smoke-test HTTP 200 on port 8501 |
| **Deploy — Tag & Report** | Phase 4 | Tag image as `latest`, print deployment instructions |

### Start Jenkins locally

```bash
docker compose up -d jenkins
# → http://localhost:8080
```

### First-time setup (one-time only)

1. Get the admin password:
   ```bash
   docker compose logs jenkins | grep -A2 "Please use"
   ```
2. Paste into http://localhost:8080 → **Install suggested plugins** → create admin user
3. Install extra plugins: **Manage Jenkins → Plugins → Available**: `Docker Pipeline`, `Git`
4. Auto-create the pipeline job:
   - **Manage Jenkins → Script Console**
   - Paste contents of [`jenkins/create-pipeline-job.groovy`](jenkins/create-pipeline-job.groovy)
   - Click **Run**
5. Click **Build Now** — all 4 stages run automatically

Jenkins polls GitHub every 5 minutes — any push to `main` triggers the pipeline.

---

## 🔌 FastAPI Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/analyse` | Run AI financial analysis |
| `POST` | `/transaction` | Log a transaction |
| `GET` | `/transactions` | List all transactions |
| `GET` | `/spending` | Spending breakdown by category |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit 1.40+ |
| **Charts** | Plotly (candlestick, pie, bar, line) |
| **Market Data** | yfinance |
| **Technical Indicators** | pandas-ta |
| **AI Orchestration** | CrewAI + LiteLLM |
| **LLM Providers** | Groq (free) · Anthropic Claude |
| **Backend API** | FastAPI + Uvicorn |
| **Database** | SQLite (via `aiosqlite`) |
| **Validation** | Pydantic v2 |
| **Containerisation** | Docker + Docker Compose |
| **CI/CD** | Jenkins (4-stage ADLC pipeline) |
| **Deployment** | Streamlit Community Cloud |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests cover all 6 time-value-of-money calculator functions with edge-case inputs.

---

## 🗂️ Key Config Files

| File | Purpose |
|------|---------|
| [`config/agents.yaml`](config/agents.yaml) | Agent role, goal, and backstory for all 3 AI agents |
| [`config/tasks.yaml`](config/tasks.yaml) | Task descriptions and expected outputs |
| [`docker-compose.yml`](docker-compose.yml) | Jenkins (port 8080) + App (port 8501) service definitions |
| [`Dockerfile`](Dockerfile) | Python 3.12-slim image, installs requirements, runs Streamlit on 8501 |
| [`Jenkinsfile`](Jenkinsfile) | 4-stage CI/CD pipeline (ADLC: Plan → Design → Execute → Deploy) |
| [`.env.example`](.env.example) | Environment variable template (copy to `.env`, fill in keys) |
| [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example) | Streamlit Cloud secrets template |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run `pytest tests/ -v` to verify
5. Push and open a Pull Request

---

*Digital Smart Finance Tracker v5 · Quartet Protocol · AI Agentic Systems Bootcamp*
