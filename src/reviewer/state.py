import operator
from typing import Annotated, TypedDict

from .models import Finding


class ReviewState(TypedDict):
    repo: str                       # e.g. "owner/name"
    pr_number: int
    diff_files: list[dict]          # filled by the fetch node
    reviewers_to_run: list[str]     # filled by the triage node
    findings: Annotated[list[Finding], operator.add]  # added to by the reviewers
    final_findings: list[Finding]   # filled by the verifier