"""
custom_tools.py — Custom BaseTool implementations for Smart Digital Finance Tracker.
SafeQueryTool: read-only SQL guardrail.
WebScraperTool: direct URL content fetcher.
ContextWriterTool: writes to the Semantic Vault (context_notes.txt).
"""
import sqlite3
import requests
import logging
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class SafeQueryTool(BaseTool):
    name: str = "database_query_tool"
    description: str = (
        "Read-only SQL query tool for memory.db (finance database). "
        "Use SELECT statements only — tables: transactions, budgets, run_history, knowledge_items. "
        "Never use DROP, DELETE, UPDATE, or INSERT. "
        "Always use SUM() for totals, never COUNT(*) for amounts."
    )

    def _run(self, query: str) -> str:
        blocked = ['DROP', 'DELETE', 'UPDATE', 'INSERT']
        if any(k in query.upper() for k in blocked):
            raise ValueError("Action Prohibited: Read Only Access")
        try:
            conn = sqlite3.connect("memory.db")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            return f"Retrieved data: {results}"
        except Exception as e:
            return f"Database Error: {e}"


class WebScraperTool(BaseTool):
    name: str = "web_scraper_tool"
    description: str = (
        "Fetches raw HTML content from a given URL. "
        "Use when you need to read the full content of a specific financial resource or web page."
    )

    def _run(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text[:5000]
        except Exception as e:
            return f"Scrape Error: {e}"


class ContextWriterTool(BaseTool):
    name: str = "context_writer_tool"
    description: str = (
        "Writes financial research notes to context_notes.txt (Semantic Vault). "
        "Use to save important financial findings, advice, or context for later retrieval."
    )

    def _run(self, content: str) -> str:
        try:
            with open("context_notes.txt", "a", encoding="utf-8") as f:
                f.write(content + "\n\n")
            return "Context saved to Semantic Vault."
        except Exception as e:
            return f"Write Error: {e}"
