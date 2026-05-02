"""
crew.py — Core Orchestration Script for Smart Digital Finance Tracker.
A-A-R Pipeline: Analyse Expenses -> Advise -> Report
"""
import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel
from crewai.tools import BaseTool
from crewai_tools import FileReadTool, SerperDevTool

from src.tools.custom_tools import SafeQueryTool, WebScraperTool, ContextWriterTool
from src.tools.database import setup_knowledge_db, save_run
from src.tools.resilience import (
    execute_with_retry,
    apply_budget_cap,
    StructuredReport,
    create_reviewer_agent,
)
from src.tools.debug_tools import ExecutionTracer, run_smoke_test

CONFIG_DIR = Path(__file__).parent.parent / "config"
tracer = ExecutionTracer()


# ── LLM: Anthropic Claude (via CrewAI's LiteLLM wrapper) ──────────────────────
# Model can be overridden via CLAUDE_MODEL env var. Default: Sonnet — best
# quality/cost balance for financial reasoning.
_CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "anthropic/claude-sonnet-4-6")
claude_llm = LLM(
    model=_CLAUDE_MODEL,
    temperature=0.3,
    max_tokens=1500,   # kept low to stay within Groq free-tier 6 k TPM limit
)

# ── Serper web search is optional — only enable if SERPER_API_KEY is set ─────
def _serper_if_available():
    key = os.environ.get("SERPER_API_KEY", "")
    if key and not key.startswith("your_"):
        return SerperDevTool()
    logger.info("SERPER_API_KEY not set — web search disabled; agents will rely on DB + context.")
    return None


def _load_config(filename: str) -> dict:
    config_path = CONFIG_DIR / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def build_crew(user_topic: str) -> Crew:
    agents_cfg = _load_config("agents.yaml")
    tasks_cfg  = _load_config("tasks.yaml")

    search_tool    = _serper_if_available()
    file_read_tool = FileReadTool(file_path="context_notes.txt")
    sql_tool       = SafeQueryTool()
    scraper_tool   = WebScraperTool()
    ctx_writer_tool = ContextWriterTool()

    analyst_tools = [scraper_tool, sql_tool, file_read_tool]
    if search_tool is not None:
        analyst_tools.insert(0, search_tool)

    expense_analyst = Agent(
        role      = agents_cfg["expense_analyst"]["role"],
        goal      = agents_cfg["expense_analyst"]["goal"],
        backstory = agents_cfg["expense_analyst"]["backstory"],
        tools     = analyst_tools,
        llm       = claude_llm,
        verbose   = True,
        allow_delegation = False,
    )

    financial_advisor = Agent(
        role      = agents_cfg["financial_advisor"]["role"],
        goal      = agents_cfg["financial_advisor"]["goal"],
        backstory = agents_cfg["financial_advisor"]["backstory"],
        tools     = [sql_tool, file_read_tool],
        llm       = claude_llm,
        verbose   = True,
        allow_delegation = False,
    )

    report_writer = Agent(
        role      = agents_cfg["report_writer"]["role"],
        goal      = agents_cfg["report_writer"]["goal"],
        backstory = agents_cfg["report_writer"]["backstory"],
        tools     = [ctx_writer_tool],
        llm       = claude_llm,
        verbose   = True,
        allow_delegation = False,
    )

    for agent in [expense_analyst, financial_advisor, report_writer]:
        apply_budget_cap(agent, max_tokens=1500)

    expense_analysis_task = Task(
        description     = tasks_cfg["expense_analysis_task"]["description"].format(user_topic=user_topic),
        expected_output = tasks_cfg["expense_analysis_task"]["expected_output"],
        agent           = expense_analyst,
    )

    advice_task = Task(
        description     = tasks_cfg["advice_task"]["description"].format(user_topic=user_topic),
        expected_output = tasks_cfg["advice_task"]["expected_output"],
        agent           = financial_advisor,
        context         = [expense_analysis_task],
        output_json     = StructuredReport,
    )

    report_task = Task(
        description     = tasks_cfg["report_task"]["description"].format(user_topic=user_topic),
        expected_output = tasks_cfg["report_task"]["expected_output"],
        agent           = report_writer,
        context         = [expense_analysis_task, advice_task],
    )

    # Memory disabled: CrewAI's default memory needs an OpenAI embedder.
    # We get clean multi-agent sequential execution without it; can re-enable
    # later with a local embedder (e.g. sentence-transformers) if needed.
    crew = Crew(
        agents  = [expense_analyst, financial_advisor, report_writer],
        tasks   = [expense_analysis_task, advice_task, report_task],
        process = Process.sequential,
        memory  = False,
        verbose = True,
    )
    return crew


def run_crew(user_topic: str) -> str:
    tracer.start_mission(user_topic)
    try:
        setup_knowledge_db()
        logger.info(f"Starting A-A-R Pipeline for topic: '{user_topic}'")
        crew   = build_crew(user_topic)
        result = execute_with_retry(
            lambda: str(crew.kickoff(inputs={"user_topic": user_topic})),
            max_retries=3,
        )
        save_run(user_topic=user_topic, result=result, status="success")
        tracer.log_agent_action("Crew", "kickoff complete", tool_used="A-A-R Pipeline")
        tracer.end_mission(status="success")
        return result
    except Exception as e:
        logger.error(f"Analysis Failed: {e}")
        save_run(user_topic=user_topic, result=str(e), status="failed")
        tracer.end_mission(status="failed")
        return f"Analysis Failed: {e}"
    finally:
        logger.info("Finance analysis complete.")


if __name__ == "__main__":
    run_smoke_test()
    output = run_crew("How can I reduce my monthly food spending?")
    print(output)
