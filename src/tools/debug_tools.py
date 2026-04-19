"""
debug_tools.py — Debugging, Tracing & Diagnostics Toolkit for Smart Digital Finance Tracker.
"""
import os
import sys
import time
import sqlite3
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

logger = logging.getLogger(__name__)


def run_smoke_test() -> dict:
    """Environment Diagnostics Table — run before every deployment."""
    results = {}

    # Python version
    py_version = sys.version_info
    results["Python >= 3.12"] = (
        py_version >= (3, 12),
        f"Found Python {py_version.major}.{py_version.minor}.{py_version.micro}"
    )

    # API keys
    for key in ["OPENAI_API_KEY", "SERPER_API_KEY"]:
        val = os.environ.get(key, "")
        results[f"Env: {key}"] = (
            bool(val),
            "SET" if val else "MISSING — add to .env file"
        )

    # Required files
    base = Path(__file__).parent.parent.parent
    required_files = [
        "src/crew.py",
        "src/tools/custom_tools.py",
        "src/tools/database.py",
        "src/tools/resilience.py",
        "config/agents.yaml",
        "config/tasks.yaml",
        "app/streamlit_app.py",
        "app/main.py",
        ".env",
        "requirements.txt",
    ]
    for f in required_files:
        exists = (base / f).exists()
        results[f"File: {f}"] = (exists, "Found" if exists else "MISSING")

    # Database
    try:
        conn = sqlite3.connect("memory.db")
        conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        conn.close()
        results["DB: memory.db"] = (True, "Accessible")
    except Exception as e:
        results["DB: memory.db"] = (False, f"Error: {e}")

    # Core imports
    for pkg in ["crewai", "streamlit", "fastapi", "pydantic", "yaml", "dotenv"]:
        try:
            __import__(pkg)
            results[f"Import: {pkg}"] = (True, "OK")
        except ImportError:
            results[f"Import: {pkg}"] = (False, f"NOT INSTALLED — run: pip install {pkg}")

    print("\n" + "=" * 60)
    print(" SMOKE TEST — Environment Diagnostics (Smart Finance Tracker)")
    print("=" * 60)
    passed_count = 0
    for check, (ok, detail) in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {check:<40} {detail}")
        if ok:
            passed_count += 1
    print("=" * 60)
    print(f"  Result: {passed_count}/{len(results)} checks passed")
    print("=" * 60 + "\n")
    return results


class ExecutionTracer:
    """Records timing, tool usage, and decision flow for every crew run."""

    def __init__(self):
        self.traces = []
        self.start_time: Optional[float] = None

    def start_mission(self, topic: str):
        self.start_time = time.time()
        self.traces = []
        logger.info(f"[TRACE] Finance analysis started: '{topic}'")

    def log_agent_action(self, agent_role: str, action: str, tool_used: Optional[str] = None):
        entry = {
            "event": "AGENT_ACTION",
            "timestamp": datetime.now().isoformat(),
            "agent_role": agent_role,
            "action": action,
            "tool_used": tool_used or "none",
            "elapsed_s": round(time.time() - (self.start_time or time.time()), 2),
        }
        self.traces.append(entry)
        logger.info(f"[TRACE] {agent_role} -> {action}" + (f" (tool: {tool_used})" if tool_used else ""))

    def end_mission(self, status: str = "success"):
        elapsed = round(time.time() - (self.start_time or time.time()), 2)
        logger.info(f"[TRACE] Analysis ended — status: {status}, elapsed: {elapsed}s")
        print("\n" + "=" * 60)
        print(" EXECUTION TRACE (Decision Flow)")
        print("=" * 60)
        for t in self.traces:
            if t["event"] == "AGENT_ACTION":
                print(f"  [{t['elapsed_s']:>6}s]  {t['agent_role']:<25} -> {t['action']}")
                if t["tool_used"] != "none":
                    print(f"  {'':25}     Tool: {t['tool_used']}")
        print("-" * 60)
        print(f"  Total elapsed : {elapsed}s")
        print(f"  Final status  : {status.upper()}")
        print("=" * 60 + "\n")


def run_golive_checklist() -> bool:
    """Final verification before deploying to production."""
    base = Path(__file__).parent.parent.parent
    checks = []

    print("\n" + "=" * 60)
    print(" GO-LIVE CHECKLIST (Smart Digital Finance Tracker)")
    print("=" * 60)

    def check(label: str, passed: bool, fix: str = ""):
        icon = "OK" if passed else "FAIL"
        print(f"  {icon}  {label}")
        if not passed and fix:
            print(f"       FIX: {fix}")
        checks.append(passed)

    check("src/ directory exists", (base / "src").is_dir())
    check("config/ directory exists", (base / "config").is_dir())
    check("tests/ directory exists", (base / "tests").is_dir())
    check("config/agents.yaml present", (base / "config/agents.yaml").exists())
    check("config/tasks.yaml present", (base / "config/tasks.yaml").exists())

    gitignore = (base / ".gitignore").read_text() if (base / ".gitignore").exists() else ""
    check(".env in .gitignore", ".env" in gitignore, "Add .env to .gitignore")
    check("memory.db in .gitignore", "memory.db" in gitignore, "Add memory.db to .gitignore")
    check("requirements.txt present", (base / "requirements.txt").exists())
    check("README.md present", (base / "README.md").exists())

    all_passed = all(checks)
    print("-" * 60)
    print(f"  Result: {'READY FOR DEPLOYMENT' if all_passed else 'NOT READY — fix issues above'}")
    print("=" * 60 + "\n")
    return all_passed


if __name__ == "__main__":
    run_smoke_test()
    run_golive_checklist()
