"""
database.py — SQLite storage for Smart Digital Finance Tracker.
Sets up finance.db and provides save/query helpers.
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

DEFAULT_DB = "memory.db"


def setup_knowledge_db(db_path: str = DEFAULT_DB):
    """Creates all required tables in memory.db if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT,
            amount      REAL,
            category    TEXT,
            description TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT,
            budget_limit REAL,
            period      TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_topic  TEXT,
            result      TEXT,
            status      TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            key         TEXT,
            value       TEXT,
            category    TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    logger.info("memory.db initialised with all finance tables.")


def save_run(user_topic: str, result: str, status: str, db_path: str = DEFAULT_DB):
    """Saves a crew run result to the run_history table."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO run_history (user_topic, result, status) VALUES (?, ?, ?)",
            (user_topic, result, status)
        )
        conn.commit()
        conn.close()
        logger.info(f"Run saved to DB — topic: '{user_topic}', status: {status}")
    except Exception as e:
        logger.error(f"Failed to save run to DB: {e}")


def save_transaction(date: str, amount: float, category: str, description: str,
                     db_path: str = DEFAULT_DB):
    """Saves a financial transaction to the transactions table."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO transactions (date, amount, category, description) VALUES (?, ?, ?, ?)",
            (date, amount, category, description)
        )
        conn.commit()
        conn.close()
        logger.info(f"Transaction saved: {category} £{amount}")
    except Exception as e:
        logger.error(f"Failed to save transaction: {e}")


def get_transactions(db_path: str = DEFAULT_DB) -> list:
    """Retrieves all transactions ordered by date descending."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT date, amount, category, description FROM transactions ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Failed to retrieve transactions: {e}")
        return []


def get_spending_by_category(db_path: str = DEFAULT_DB) -> list:
    """Returns total spending grouped by category using SUM()."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM transactions GROUP BY category ORDER BY total DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Failed to retrieve spending by category: {e}")
        return []
