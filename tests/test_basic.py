"""
Basic smoke tests for Smart Digital Finance Tracker.
"""
import pytest
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools.database import setup_knowledge_db, save_run, save_transaction, get_transactions, get_spending_by_category


TEST_DB = "test_memory.db"


@pytest.fixture(autouse=True)
def clean_db():
    """Create a fresh test DB before each test and remove it after."""
    setup_knowledge_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_setup_creates_tables():
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()
    assert "transactions" in tables
    assert "budgets" in tables
    assert "run_history" in tables
    assert "knowledge_items" in tables


def test_save_and_retrieve_transaction():
    save_transaction("2026-04-19", 45.50, "Food & Dining", "Groceries", TEST_DB)
    rows = get_transactions(TEST_DB)
    assert len(rows) == 1
    assert rows[0][1] == 45.50
    assert rows[0][2] == "Food & Dining"


def test_spending_by_category():
    save_transaction("2026-04-19", 45.50, "Food & Dining", "Groceries", TEST_DB)
    save_transaction("2026-04-18", 20.00, "Transport", "Bus pass", TEST_DB)
    save_transaction("2026-04-17", 30.00, "Food & Dining", "Restaurant", TEST_DB)
    totals = get_spending_by_category(TEST_DB)
    totals_dict = {row[0]: row[1] for row in totals}
    assert totals_dict["Food & Dining"] == pytest.approx(75.50)
    assert totals_dict["Transport"] == pytest.approx(20.00)


def test_save_run():
    save_run("test topic", "test result", "success", TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT user_topic, status FROM run_history")
    rows = cursor.fetchall()
    conn.close()
    assert len(rows) == 1
    assert rows[0][0] == "test topic"
    assert rows[0][1] == "success"
