from typing import TypedDict, List, Optional


class ReviewState(TypedDict):
    diff: str
    files_changed: List[str]

    workers_to_run: List[str]

    bug_findings: Optional[str]
    style_findings: Optional[str]
    security_findings: Optional[str]

    final_verdict: Optional[str]
    errors: List[str]