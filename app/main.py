"""
main.py — FastAPI Interface Layer for Smart Digital Finance Tracker.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from src.crew import run_crew
from src.tools.database import setup_knowledge_db, save_run, save_transaction, get_transactions, get_spending_by_category

app = FastAPI(
    title="Smart Digital Finance Tracker API",
    description="FastAPI interface for the A-A-R CrewAI finance analysis pipeline.",
    version="1.0.0",
)

setup_knowledge_db()


@app.get("/")
def health_check():
    return {"status": "online", "service": "Smart Digital Finance Tracker API"}


@app.post("/analyse")
def analyse(data: dict):
    user_topic = data.get("user_topic", "").strip()
    if not user_topic:
        return {"status": "error", "result": "user_topic is required"}
    try:
        result = run_crew(user_topic)
        save_run(user_topic=user_topic, result=result, status="success")
        return {"status": "success", "result": result}
    except Exception as e:
        save_run(user_topic=user_topic, result=str(e), status="failed")
        return {"status": "error", "result": f"Analysis Failed: {e}"}


@app.post("/transaction")
def add_transaction(data: dict):
    """Add a financial transaction to the database."""
    try:
        save_transaction(
            date=data.get("date", ""),
            amount=float(data.get("amount", 0)),
            category=data.get("category", "Other"),
            description=data.get("description", ""),
        )
        return {"status": "success", "message": "Transaction saved."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/transactions")
def list_transactions():
    """Return all transactions."""
    rows = get_transactions()
    return {
        "status": "success",
        "transactions": [
            {"date": r[0], "amount": r[1], "category": r[2], "description": r[3]}
            for r in rows
        ],
    }


@app.get("/spending")
def spending_by_category():
    """Return total spending grouped by category."""
    rows = get_spending_by_category()
    return {
        "status": "success",
        "spending": [{"category": r[0], "total": r[1]} for r in rows],
    }


# Legacy endpoint alias for compatibility
@app.post("/kickoff")
def kickoff(data: dict):
    return analyse(data)
