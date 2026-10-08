from langchain_groq import ChatGroq

from ..config import GROQ_API_KEY
from ..diff import annotate_patch
from ..models import Finding, ReviewResult, TriageResult
from ..prompts import SECURITY_PROMPT, BUG_PROMPT, MAINTAINABILITY_PROMPT, TRIAGE_PROMPT
from ..state import ReviewState

MODEL = "openai/gpt-oss-120b"
MAX_DIFF_CHARS = 12000


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

def review_files(diff_files: list[dict], system_prompt: str, category: str) -> list[Finding]:
    diff_text = build_prompt(diff_files)
    if not diff_text:
        return []
    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY, temperature=0)
    reviewer = llm.with_structured_output(ReviewResult)
    result = reviewer.invoke([("system", system_prompt), ("human", diff_text)])
    for f in result.findings:
        f.category = category  # trust our routing, not the model's labeling
    return result.findings


def security_node(state: ReviewState) -> dict:
    return {"findings": review_files(state["diff_files"], SECURITY_PROMPT, "security")}


def bug_node(state: ReviewState) -> dict:
    return {"findings": review_files(state["diff_files"], BUG_PROMPT, "bug")}


def maintainability_node(state: ReviewState) -> dict:
    return {"findings": review_files(state["diff_files"], MAINTAINABILITY_PROMPT, "maintainability")}



def triage_node(state: ReviewState) -> dict:
    diff_text = build_prompt(state["diff_files"])
    if not diff_text:
        return {"reviewers_to_run": []}
    llm = ChatGroq(model=MODEL, api_key=GROQ_API_KEY, temperature=0)
    triage = llm.with_structured_output(TriageResult)
    result = triage.invoke([("system", TRIAGE_PROMPT), ("human", diff_text)])
    return {"reviewers_to_run": result.reviewers_to_run}