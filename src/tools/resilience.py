"""
resilience.py — 4-Layer Resilience Stack for Smart Digital Finance Tracker.
Layer 1: Exponential backoff retry
Layer 2: Token budget cap
Layer 3: JSON schema enforcement (Pydantic)
Layer 4: Reviewer agent metacognition
"""
import time
import random
import json
import logging
from typing import Callable, Any, Optional, List
from pydantic import BaseModel, ValidationError
from crewai import Agent, Task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("finance_tracker.log"),
    ]
)
logger = logging.getLogger(__name__)


# Layer 1: Retry ----------------------------------------------------------------

def execute_with_retry(api_call_func: Callable, max_retries: int = 3) -> Any:
    """Exponential backoff + jitter retry wrapper.

    Rate-limit (429) errors get a longer 60-second wait so the provider
    token-per-minute window resets before the next attempt.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            return api_call_func()
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            # 429 / rate-limit: wait for provider window to reset (60 s)
            if "429" in err_str or "rate_limit" in err_str or "rate limit" in err_str:
                wait_time = 65 + random.uniform(0, 5)
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} — rate-limited (429). "
                    f"Waiting {wait_time:.0f}s for provider window to reset..."
                )
            else:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                    f"Retrying in {wait_time:.2f}s..."
                )
            time.sleep(wait_time)
    raise Exception(f"Layer 1 Failure: Max retries exceeded. Last error: {last_error}")


# Layer 2: Budget Cap -----------------------------------------------------------

MAX_TOKENS_PER_CALL = 5000


def apply_budget_cap(agent: Agent, max_tokens: int = MAX_TOKENS_PER_CALL) -> Agent:
    """Applies a token budget cap to an agent to prevent runaway costs."""
    if hasattr(agent, 'llm') and agent.llm:
        agent.llm.max_tokens = max_tokens
        logger.info(f"[Layer 2] Budget cap applied: {max_tokens} tokens on '{agent.role}'")
    return agent


def check_query_budget(query: str, max_length: int = 2000) -> bool:
    """Rejects inputs that exceed the character budget."""
    if len(query) > max_length:
        logger.warning(f"[Layer 2] Query rejected: {len(query)} chars exceeds {max_length}")
        return False
    return True


# Layer 3: JSON Schema ----------------------------------------------------------

class StructuredFinanceReport(BaseModel):
    """JSON schema for structured financial analysis output (Layer 3)."""
    title: str
    summary: str
    findings: List[str]
    recommendations: List[str]
    status: str  # "complete" | "partial" | "failed"


# Keep alias so crew.py import works with either name
StructuredReport = StructuredFinanceReport


def validate_json_output(raw_output: str, schema: type = StructuredFinanceReport) -> Optional[dict]:
    """Validates and parses JSON output from agents against the Pydantic schema."""
    try:
        data = json.loads(raw_output)
        validated = schema(**data)
        logger.info("[Layer 3] JSON output validated successfully.")
        return validated.model_dump()
    except json.JSONDecodeError as e:
        logger.error(f"[Layer 3] JSON parse error: {e}")
        return None
    except ValidationError as e:
        logger.error(f"[Layer 3] Schema validation error: {e}")
        return None


# Layer 4: Reviewer Agent -------------------------------------------------------

def create_reviewer_agent() -> Agent:
    """Creates a metacognition reviewer agent that fact-checks financial outputs."""
    return Agent(
        role="Financial Quality Reviewer",
        goal=(
            "Ensure accuracy of the financial report by critiquing the writer's output "
            "against the original expense analysis and advice. "
            "Flag any fabricated figures or unsupported financial claims."
        ),
        backstory=(
            "You are a meticulous financial fact-checker. Your only job is to compare "
            "the draft financial report against the original data analysis and advisory "
            "context, and identify any discrepancies or invented numbers. "
            "Output either APPROVED or a numbered list of corrections."
        ),
        verbose=True,
        allow_delegation=False,
    )
