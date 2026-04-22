# 💰 Digital Smart Finance Tracker v5

> **Quartet Protocol — Mission Charlie: Analyst + Reporting Engine.**
> A real-time stock & crypto dashboard + AI financial analysis + loan rate tracker + time-value-of-money calculator — all in one Streamlit app, containerised with Docker.

---

## 🌟 What Is This App?

The **Digital Smart Finance Tracker v5** is a full-stack personal finance and investment platform built for the Week 19 Capstone (Mission Charlie — The Insight Engine). It pulls live market data for any stock or cryptocurrency, renders interactive candlestick charts, runs an AI analysis engine, tracks major-loan interest rates at daily/weekly/monthly resolution, and includes a full time-value-of-money calculator ported from the original Colab notebook.

No finance jargon. No technical setup for end users. Just enter a ticker or tweak an APR, and get answers.

---

## 📸 App Overview

| Tab | What It Does |
|---|---|
| 📈 **Markets** | Live candlestick chart, volume, moving averages, key metrics for any stock or crypto |
| 🤖 **AI Analysis** | Ask any finance question — get a structured, professional report in 1–3 minutes |
| 📊 **My Finances** | Major loan rates (daily/weekly/monthly) + spending breakdown with pie chart and history |
| ➕ **Add Transaction** | Log daily expenses with date, amount, category, and description |
| 🧮 **Calculator** | Simple & compound interest, Future Value, Present Value, FV & PV Annuities — with growth charts |

---

## 🧮 Calculator — Time Value of Money

Six financial formulas, each with inputs, a result card, and a growth chart:

| Formula | Used for |
|---|---|
| Simple Interest `I = P·r·t` | Short-term loans, bonds |
| Compound Interest `A = P(1+r/n)^(n·t)` | Savings, deposits |
| Future Value | "What will my money be worth?" |
| Present Value | "What's this future payout worth today?" |
| FV Annuity | Retirement saving, SIPs |
| PV Annuity | Loan principal from repayments |

All compounding frequencies supported: annual, semi-annual, quarterly, monthly, weekly, daily.

---

## 🏦 Loan Rate Tracker (My Finances tab)

Editable table of 9 major loan types (mortgage, auto, personal, credit card, student, HELOC, payday) with:

- Daily / Weekly / Monthly effective rate (APR ÷ 365, 52, 12)
- Daily / Weekly / Monthly / Yearly interest cost on your principal
- Grouped bar chart comparing interest cost across loan types

Edit any APR or principal → table and chart recalculate instantly.

---

## 📈 Markets — Real-Time Charts

Type any ticker and instantly get:

- **Candlestick price chart** with volume bars — green for up, red for down
- **Moving averages** — MA20 and MA50 overlaid on the price line
- **Key metrics** — current price, % change, market cap, 52-week high/low
- **Company summary** — expandable overview of the business
- **Configurable period & interval** — from 1 month to 5 years, daily to monthly

Supported assets include stocks, ETFs, indices, and cryptocurrencies:

```
AAPL   GOOGL   AMZN   TSLA   NVDA   MSFT
BTC-USD   ETH-USD   SOL-USD   BNB-USD
^GSPC (S&P 500)   ^DJI (Dow Jones)   ^IXIC (NASDAQ)
```

Quick-pick buttons in the sidebar for the most popular tickers.

---

## 🤖 AI Analysis — Powered by a 3-Agent Pipeline

Behind the scenes, a silent AI crew analyses your query using three specialised agents working in sequence:

```
Expense Analyst  ──►  Financial Advisor  ──►  Report Writer
```

What the user sees: a clean text input and a professional financial report.
What happens behind the scenes: real-time web research, database queries, cross-referenced financial advice, and structured report generation.

Every report is structured as:
1. **Overview** — summary of the financial situation
2. **Key Findings** — at least 3 data-grounded insights
3. **Recommendations** — prioritised action list
4. **Action Plan** — specific next steps

Reports are downloadable as `.md` files.

---

## 📊 Personal Finance Tracking

- Log transactions by category: Food & Dining, Transport, Housing, Entertainment, Healthcare, Shopping, Utilities, Savings, Investments, Subscriptions
- Interactive **donut pie chart** showing spending distribution
- Full **transaction history** table
- Summary metrics: total spent, number of transactions, top spending category

---

## 🏗️ Project Structure

```
smart-finance-tracker/
├── app/
│   ├── streamlit_app.py     # Full dashboard — 4 tabs, charts, AI analysis
│   └── main.py              # FastAPI backend (5 endpoints)
├── src/
│   ├── crew.py              # AI orchestration (A-A-R pipeline)
│   └── tools/
│       ├── database.py      # SQLite — transactions, budgets, run history
│       ├── custom_tools.py  # SQL guardrail, web scraper, context writer
│       ├── resilience.py    # 4-layer resilience stack
│       └── debug_tools.py   # Smoke test & execution tracer
├── config/
│   ├── agents.yaml          # Agent definitions
│   └── tasks.yaml           # Task definitions
├── tests/
│   └── test_basic.py        # Pytest test suite
├── Dockerfile
├── docker-compose.yml       # Jenkins + App
├── Jenkinsfile              # CI/CD pipeline
└── requirements.txt
```

---

## 🛡️ Resilience & Reliability

| Layer | Protection |
|---|---|
| **L1 — Retry** | Exponential backoff with jitter — up to 3 retries on API failure |
| **L2 — Budget Cap** | `max_tokens=5000` per agent call — prevents runaway API costs |
| **L3 — Schema Enforcement** | Pydantic model validates all structured JSON outputs |
| **L4 — Reviewer** | Fact-checking agent verifies report accuracy before delivery |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12 (not 3.13+ — required by AI dependencies)
- OpenAI API key → [platform.openai.com](https://platform.openai.com)
- Serper API key → [serper.dev](https://serper.dev)

### 1. Clone & Set Up

```bash
git clone https://github.com/aftonis/smart-finance-tracker.git
cd smart-finance-tracker
```

### 2. Create Virtual Environment with Python 3.12

```bash
# Windows
"C:\Users\<YourName>\AppData\Local\Programs\Python\Python312\python.exe" -m venv venv
venv\Scripts\activate
```

### 3. Add Your API Keys

Copy `.env.example` to `.env` and fill in:

```env
OPENAI_API_KEY=sk-proj-...
SERPER_API_KEY=...
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the App

```bash
streamlit run app/streamlit_app.py
```

Opens at **http://localhost:8501**

---

## 🐳 Docker + Jenkins CI/CD

```bash
# Start Jenkins + app containers
docker compose up -d

# Verify
docker ps

# Jenkins dashboard
open http://localhost:8080

# Stop everything
docker compose down
```

**Jenkins pipeline stages:**
1. `Checkout` — pulls latest code
2. `Install Dependencies` — pip install
3. `Test` — pytest
4. `Docker Build` — builds container
5. `Push to GitHub` — triggers Streamlit Cloud redeploy

---

## ☁️ Streamlit Cloud Deployment

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect `aftonis/smart-finance-tracker`
3. Main file: `app/streamlit_app.py`
4. Add secrets in **Advanced settings**:
   ```
   OPENAI_API_KEY = "sk-proj-..."
   SERPER_API_KEY = "..."
   ```
5. Click **Deploy**

Every `git push origin master` triggers an automatic redeploy.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/analyse` | Run AI financial analysis |
| `POST` | `/transaction` | Log a transaction |
| `GET` | `/transactions` | List all transactions |
| `GET` | `/spending` | Spending by category |

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit 1.56+ |
| **Charts** | Plotly (candlestick, pie, line) |
| **Market Data** | yfinance (stocks, crypto, indices) |
| **Technical Indicators** | pandas-ta |
| **AI Orchestration** | CrewAI |
| **Backend API** | FastAPI + Uvicorn |
| **Database** | SQLite |
| **Validation** | Pydantic v2 |
| **CI/CD** | Jenkins (Docker) |
| **Deployment** | Streamlit Cloud |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📋 Daily Workflow

```bash
# Activate environment
venv\Scripts\activate

# Run the app
streamlit run app/streamlit_app.py

# Push changes
git add .
git commit -m "Your message"
git push origin master
```

---

*Smart Digital Finance Tracker · Blueprint Blue · AI Agentic Systems Bootcamp*
