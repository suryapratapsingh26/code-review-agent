import time

from groq import RateLimitError, BadRequestError
from langchain_groq import ChatGroq

from src.reviewer.config import GROQ_API_KEY
from src.reviewer.diff import annotate_patch
from src.reviewer.models import Finding, ReviewResult

MODEL = "openai/gpt-oss-120b"
MAX_DIFF_CHARS = 12000


def _invoke_with_retry(structured_llm, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return structured_llm.invoke(messages)
        except (RateLimitError, BadRequestError):
            if attempt == max_retries - 1:
                raise
            wait = 20 * (attempt + 1)
            print(f"  (rate limited, waiting {wait}s before retry...)")
            time.sleep(wait)
BASELINE_PROMPT = """You are a careful senior engineer reviewing a pull request.

You are given the diff of each changed file. Every line has its line number in the NEW file.

Rules:
- Only report real problems in the added lines (lines starting with +).
- Use the exact file path and the line number shown next to the problem.
- Categories: security, bug, maintainability.
- Severity: high = will break or is exploitable, medium = likely problem, low = minor.
- Do not comment on style or formatting. Do not invent problems.
- If the diff looks fine, return an empty list.
"""


def build_prompt(diff_files: list[dict]) -> str:
    parts = []
    total = 0
    for f in diff_files:
        if not f.get("patch"):
            continue
        block = f"File: {f['filename']}\n{annotate_patch(f['patch'])}\n"
        if total + len(block) > MAX_DIFF_CHARS:
            break
        parts.append(block)
        total += len(block)
    return "\n".join(parts)


def baseline_review(diff_files: list[dict]) -> list[Finding]:
    """One LLM call, one general prompt, no triage/parallel/verifier."""
    diff_text = build_prompt(diff_files)
    if not diff_text:
        return []
    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY, temperature=0)
    reviewer = llm.with_structured_output(ReviewResult)
    result = _invoke_with_retry(reviewer, [("system", BASELINE_PROMPT), ("human", diff_text)])
    return result.findings