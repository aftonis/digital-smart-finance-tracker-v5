# 💰 Smart Digital Finance Tracker

> **An AI-powered personal finance dashboard that analyses your spending, advises on your budget, and generates professional financial reports — all powered by a 3-agent CrewAI pipeline.**

---

## 🌟 Overview

The **Smart Digital Finance Tracker** is a full-stack, AI-driven financial management application built for the modern age. It combines the power of large language models, multi-agent orchestration, and real-time data visualisation to give you a complete picture of your financial health — and tell you exactly what to do about it.

Gone are the days of manually reviewing spreadsheets or guessing where your money goes. Simply log your transactions, ask the AI a finance question, and within minutes receive a structured, data-grounded financial report written by three specialised AI agents working in sequence.

This project is built on the **Blueprint Blue architecture** — a production-grade, resilient AI pipeline featuring retry logic, token budgeting, JSON schema enforcement, and reviewer metacognition. It runs locally, in Docker, and deploys publicly to Streamlit Cloud with automated CI/CD via Jenkins.

---

## 🤖 How It Works — The A-A-R Pipeline

At the heart of the app is a **3-agent CrewAI pipeline** that processes every financial query sequentially:

```
📊 Expense Analyst  ──►  💡 Financial Advisor  ──►  📝 Report Writer
     (Analyse)                  (Advise)                  (Report)
```

### Agent 1 — Expense Analyst
Digs into your transaction history stored in the SQLite database. Queries spending by category, identifies patterns and anomalies, cross-references your data with live web research (via SerperDev), and surfaces at least 3 data-grounded financial insights. Everything it reports is traceable to real data — no fabricated numbers.

### Agent 2 — Financial Advisor
Takes the analyst's findings and applies proven budgeting frameworks — including the **50/30/20 rule** and zero-based budgeting — to generate personalised, prioritised recommendations. Every piece of advice maps directly back to your actual spending data stored in the database.

### Agent 3 — Report Writer
Transforms the raw analysis and advisory notes into a polished, professional financial report (400–600 words) structured as: **Overview → Key Findings → Recommendations → Action Plan**. The report is downloadable as a Markdown file.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Live Dashboard** | Visual spending breakdown by category with interactive Plotly pie charts |
| ➕ **Transaction Logging** | Add income/expense transactions with date, amount, category, and description |
| 🤖 **AI Financial Analysis** | Ask any finance question and get a full 3-agent report in minutes |
| 📥 **Report Download** | Export your AI-generated financial report as a `.md` file |
| 🔬 **Smoke Test** | One-click environment diagnostics — checks all files, keys, imports, and DB |
| 🔧 **Debug Panel** | Live session state and environment inspector |
| 🔒 **Read-Only DB Guardrail** | SQL tool blocks all destructive queries (DROP/DELETE/UPDATE/INSERT) |
| 🔄 **Retry Resilience** | Exponential backoff retries on all API calls (up to 3 attempts) |
| 🧪 **Test Suite** | Pytest tests covering database, transactions, and run history |

---

## 🏗️ Architecture

```
smart-finance-tracker/
├── app/
│   ├── streamlit_app.py     # Main dashboard UI (3 tabs)
│   └── main.py              # FastAPI backend with 5 endpoints
├── src/
│   ├── crew.py              # CrewAI orchestration — A-A-R pipeline
│   ├── agents/
│   ├── tasks/
│   └── tools/
│       ├── database.py      # SQLite helpers (transactions, budgets, history)
│       ├── custom_tools.py  # SafeQueryTool, WebScraperTool, ContextWriterTool
│       ├── resilience.py    # 4-layer resilience stack
│       └── debug_tools.py   # Smoke test & execution tracer
├── config/
│   ├── agents.yaml          # Agent roles, goals, backstories
│   └── tasks.yaml           # Task descriptions and expected outputs
├── tests/
│   └── test_basic.py        # Pytest test suite
├── Dockerfile               # Container definition
├── docker-compose.yml       # Jenkins + App services
├── Jenkinsfile              # CI/CD pipeline (test → build → push)
└── requirements.txt         # Python dependencies
```

---

## 🛡️ 4-Layer Resilience Stack

| Layer | Protection |
|---|---|
| **L1 — Retry** | Exponential backoff with jitter — up to 3 retries on any API failure |
| **L2 — Budget Cap** | `max_tokens=5000` per agent call — prevents runaway API costs |
| **L3 — Schema Enforcement** | Pydantic model validates all structured JSON outputs |
| **L4 — Reviewer Agent** | Metacognition agent fact-checks the report against source data |

---

## 🗄️ Database Schema

The app uses **SQLite** (`memory.db`) with four tables:

| Table | Purpose |
|---|---|
| `transactions` | Stores every logged expense/income (date, amount, category, description) |
| `budgets` | Stores budget limits per category and period |
| `run_history` | Logs every AI analysis run with topic, result, and status |
| `knowledge_items` | Key-value store for persistent financial knowledge |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker Desktop (for Jenkins CI/CD)
- OpenAI API key ([platform.openai.com](https://platform.openai.com))
- Serper API key ([serper.dev](https://serper.dev))

### 1. Clone & Set Up

```bash
git clone https://github.com/aftonis/smart-finance-tracker.git
cd smart-finance-tracker

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and fill in your keys:

```env
OPENAI_API_KEY=sk-proj-...
SERPER_API_KEY=...
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard

```bash
streamlit run app/streamlit_app.py
```

Opens at **http://localhost:8501**

### 5. (Optional) Run the FastAPI Backend

```bash
uvicorn app.main:app --reload
```

API docs at **http://localhost:8000/docs**

---

## 🐳 Docker + Jenkins CI/CD

```bash
# Start Jenkins + app containers
docker compose up -d

# Verify running
docker ps

# Access Jenkins
open http://localhost:8080

# Stop everything
docker compose down
```

The **Jenkinsfile** defines a 5-stage pipeline:
1. `Checkout` — pulls latest code from GitHub
2. `Install Dependencies` — runs `pip install -r requirements.txt`
3. `Test` — runs `pytest tests/ -v`
4. `Docker Build` — builds the container image
5. `Push to GitHub` — triggers Streamlit Cloud auto-redeploy

---

## ☁️ Streamlit Cloud Deployment

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect this repository (`aftonis/smart-finance-tracker`)
3. Set **Main file path** to `app/streamlit_app.py`
4. Under **Advanced settings**, add secrets:
   ```
   OPENAI_API_KEY = "sk-proj-..."
   SERPER_API_KEY = "..."
   ```
5. Click **Deploy** — live in ~3 minutes

Every `git push origin master` automatically triggers a redeploy.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests cover:
- Database table creation
- Transaction save and retrieval
- Spending aggregation by category (using `SUM()`)
- Run history logging

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/analyse` | Run full A-A-R AI analysis |
| `POST` | `/transaction` | Log a new transaction |
| `GET` | `/transactions` | List all transactions |
| `GET` | `/spending` | Total spending by category |

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| AI Orchestration | CrewAI 0.80+ |
| LLM | OpenAI GPT (via CrewAI) |
| Web Search | SerperDev API |
| Frontend | Streamlit 1.40+ |
| Backend API | FastAPI + Uvicorn |
| Database | SQLite (via Python sqlite3) |
| Charts | Plotly Express |
| Validation | Pydantic v2 |
| CI/CD | Jenkins (Docker) |
| Deployment | Streamlit Cloud |
| Containerisation | Docker + Docker Compose |

---

## 📋 Daily Workflow

```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Run the app
streamlit run app/streamlit_app.py

# 3. Push changes
git add .
git commit -m "Your message"
git push origin master
```

---

*Smart Digital Finance Tracker · Blueprint Blue · AI Agentic Systems Bootcamp*
