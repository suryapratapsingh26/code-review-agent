from langchain_groq import ChatGroq

from ..config import GROQ_API_KEY
from ..diff import annotate_patch
from ..models import Finding, ReviewResult

MODEL = "llama-3.3-70b-versatile"
MAX_DIFF_CHARS = 12000

SYSTEM_PROMPT = """You are a careful senior engineer reviewing a pull request.

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
            continue  # binary or very large file, GitHub gives no patch
        block = f"File: {f['filename']}\n{annotate_patch(f['patch'])}\n"
        if total + len(block) > MAX_DIFF_CHARS:
            break
        parts.append(block)
        total += len(block)
    return "\n".join(parts)


def review_files(diff_files: list[dict]) -> list[Finding]:
    prompt = build_prompt(diff_files)
    if not prompt:
        return []
    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY, temperature=0)
    reviewer = llm.with_structured_output(ReviewResult)
    result = reviewer.invoke([("system", SYSTEM_PROMPT), ("human", prompt)])
    return result.findings